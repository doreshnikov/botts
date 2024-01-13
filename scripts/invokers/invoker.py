import ast
import logging
import pickle
import socket
import sys

from dataclasses import dataclass, field
from multiprocessing import Process, Queue
from typing import Any

logging.basicConfig(level=logging.INFO)


@dataclass
class Request:
    executor: str | None
    source: str
    args: tuple
    time_limit: int = field(default=1)


class Invoker:
    BATCH_SIZE = 1024

    def __init__(self, port: int):
        self.host = '0.0.0.0'
        self.port = port
        self.logger = logging.getLogger('invoker')

    def run(self, source: ast.AST, args: tuple, time_limit: int, response: dict[str, Any]):
        fn_name = None
        for node in ast.walk(source):
            if isinstance(node, ast.FunctionDef):
                fn_name = node.name
                break

        if not isinstance(source, ast.Module):
            source = ast.Module(body=[source])
        code = compile(source, filename='<ast>', mode='exec')
        evaluate = ast.parse(f'{fn_name}(*args)', mode='eval')
        expr = compile(evaluate, filename='<ast>', mode='eval')
        queue = Queue()

        # noinspection PyUnusedLocal
        def __evaluate(queue, code, expr, args):
            try:
                exec(code, globals())
            except Exception as e:
                queue.put({
                    'verdict': 'RE',
                    'message': f'could not compile: \'{e}\''
                })
                return
            try:
                value = eval(expr, globals(), locals())
                queue.put({
                    'verdict': 'OK',
                    'value': value
                })
            except Exception as e:
                message = f'runtime error \'{e}\''
                queue.put({
                    'verdict': 'RE',
                    'message': message
                })

        process = Process(target=__evaluate, args=(queue, code, expr, args))
        process.start()
        process.join(time_limit)
        if process.is_alive():
            self.logger.info('Solution timed out')
            queue.close()
            process.terminate()
            self.logger.info('Process terminated')
            response['verdict'] = 'TL'
            response['message'] = f'took more than {time_limit}s to complete'
        elif not queue.empty():
            result = queue.get()
            response.update(result)
            self.logger.info('Testing complete')

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
                data += conn.recv(Invoker.BATCH_SIZE)
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
                    ex_name = None
                    for node in ast.walk(ex):
                        if isinstance(node, ast.FunctionDef):
                            ex_name = node.name
                            break

                    src = ast.parse(source)
                    fn_name = None
                    for node in ast.walk(src):
                        if isinstance(node, ast.FunctionDef):
                            fn_name = node.name
                            break

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


if __name__ == '__main__':
    port = int(sys.argv[1])
    Invoker(port).start()
