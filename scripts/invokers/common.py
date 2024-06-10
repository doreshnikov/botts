import ast
import logging
import os
import pickle
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import socket
from multiprocessing import Process, Queue
from typing import Any
from uuid import uuid4

logging.basicConfig(level=logging.INFO)


@dataclass
class Request:
    executor: str | None
    source: str
    args: tuple
    time_limit: int = field(default=1)


class ChrootJail:
    def __init__(self):
        self.run_id = uuid4()
        self.directory = f'/tmp/run/{self.run_id}'
        os.makedirs(self.directory, exist_ok=True)

    def __enter__(self):
        os.chroot(self.directory)
        return self.directory

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.system('exit')
        shutil.rmtree(self.directory)

    @staticmethod
    def jailed(fn):
        def wrapped(*args, **kwargs):
            with ChrootJail():
                result = fn(*args, **kwargs)
                logging.info(f'Contents of jail: {os.listdir("/")}')
                return result

        return wrapped


class InvokerServiceBase(ABC):
    BATCH_SIZE = 1024

    def __init__(self, port: int):
        self.host = '0.0.0.0'
        self.port = port
        self.logger = logging.getLogger('invoker')
        self.run_id = uuid4()

    @staticmethod
    def _extract_function_name(source):
        fn_name = None
        for node in ast.walk(source):
            if isinstance(node, ast.FunctionDef):
                fn_name = node.name
                break
        return fn_name

    @abstractmethod
    def run(self, source: ast.AST, args: tuple, time_limit: int, response: dict[str, Any]):
        pass

    def validate(self, input_data: str | bytes, response: dict[str, Any]) -> Request | None:
        try:
            request = pickle.loads(input_data)
            self.logger.info(f'Received data parsed into {request}')
        except pickle.UnpicklingError as e:
            self.logger.warning(f'Request is malformed: not parseable by `pickle`, {e}')
            response['error'] = f'expected a valid pickle, got {input_data}'
            return
        if not isinstance(request, dict):
            self.logger.warning('Request is malformed: not a dictionary')
            response['error'] = f'expected a dictionary, got {request}'
            return
        if 'source' not in request or 'args' not in request:
            self.logger.warning(f'Request is malformed: not enough fields')
            response['error'] = 'expected keys \'source\' and \'args\' in request'
            return
        if not isinstance(request['args'], tuple):
            self.logger.warning(f'Request is malformed: invalid input data')
            response['error'] = f'expected request[\'args\'] to be a tuple, got {request["args"]}'
            return

        source = request['source']
        try:
            if 'executor' in request and request['executor'] is not None:
                source = request['source'] + '\n' + request['executor']
            ast.parse(source)
        except SyntaxError as e:
            self.logger.warning(f'Request is malformed: source is not a valid code but {source}')
            response['error'] = f'expected a valid code, but have {e}'
            return
        return Request(**request)

    def process(self, conn: socket.socket):
        def read(size: int):
            data = bytes()
            while len(data) < size:
                data += conn.recv(InvokerServiceBase.BATCH_SIZE)
            return data[:size]

        with conn:
            size = int.from_bytes(conn.recv(8))
            input_data = read(size)
            response = {}
            self.logger.info(f'Received request {input_data}')
            request = self.validate(input_data, response)
            if request:
                source = request.source
                if request.executor is not None:
                    ex = ast.parse(request.executor)
                    ex_name = InvokerServiceBase._extract_function_name(ex)

                    src = ast.parse(source)
                    fn_name = InvokerServiceBase._extract_function_name(src)

                    source = '\n'.join([
                        source,
                        request.executor,
                        f'{fn_name} = {ex_name}({fn_name})'
                    ])
                fn = ast.parse(source)
                self.run(fn, request.args, request.time_limit, response)
                self.logger.info(f'Run successful, response is {response}')

            response['package'] = pickle.dumps(response)
            conn.send(len(response['package']).to_bytes(8))
            conn.send(response['package'])
            conn.close()

    def start(self):
        self.logger.info('Starting service...')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            self.logger.info('Bind successful')
            while True:
                conn, addr = s.accept()
                self.logger.info(f'Connection by {addr}')
                self.process(conn)
