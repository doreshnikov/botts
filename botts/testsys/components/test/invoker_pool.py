import json
import logging
import pickle
from enum import Enum
from pathlib import Path
from queue import Queue
from socket import AF_INET, SOCK_STREAM, socket
from subprocess import Popen
from typing import Any

import docker

from botts.bot.config.local import report_fail
from botts.testsys.components.base.units import CodeUnit
from botts.testsys.components.check.checker import Verdict
from botts.testsys.components.check.generator import Arguments
from botts.testsys.components.test.invoker_base import InvokerBase, TestingResult


class Status(Enum):
    FREE = 0
    BUSY = 1


class FailedContainerException(Exception):
    def __init__(self, logs) -> None:
        super().__init__(logs)
        self.logs = logs


class SocketWrapper(InvokerBase):
    HOST = '127.0.0.1'
    CHUNK_SIZE = 1024
    INVOKER_TIMEOUT = 30

    def __init__(self, port: int, id_: str, owner: 'InvokerPool'):
        self.port = port
        self.id_ = id_
        self.owner = owner
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.settimeout(SocketWrapper.INVOKER_TIMEOUT)
        self.connected = False

    def __enter__(self):
        self.socket.connect((SocketWrapper.HOST, self.port))
        logging.getLogger('socket-wrapper').info(f'Connected on port {self.port}')
        self.connected = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.close()
        logging.getLogger('socket-wrapper').info(f'Released port {self.port}')
        self.connected = False
        self.owner.release(self.port)

    def send(self, value: Any):
        value_data = pickle.dumps(value)
        if not self.connected:
            raise ValueError('Can not operate on closed socket')
        self.socket.send(len(value_data).to_bytes(8))
        self.socket.send(value_data)

    def receive(self) -> Any:
        try:
            data = bytes()
            size = int.from_bytes(self.socket.recv(8))
            while len(data) < size:
                data += self.socket.recv(SocketWrapper.CHUNK_SIZE)
            return pickle.loads(data[:size])
        except TimeoutError as e:
            cnt = self.owner.docker_client.containers.get(self.id_)
            report_fail(f'```Invoker {self.id_}:{self.port} not responding:\n'
                        f'{cnt.logs().decode("utf-8")}```')
            return {
                'verdict': 'CF',
                'message': f'invoker failed to respond in {SocketWrapper.INVOKER_TIMEOUT}s'
            }

    def invoke(self, source: str | CodeUnit, args: Arguments, time_limit: int | float,
               executor: str | None) -> TestingResult:
        self.send({
            'executor': executor,
            'source': source,
            'args': args,
            'time_limit': time_limit
        })
        result = self.receive()
        message = result.get('message', result.get('error', None))
        return TestingResult(Verdict[result['verdict']], message, result.get('value', None))


class InvokerPool:
    def __init__(self):
        config_file = Path('./scripts/invokers/invokers.json')
        if not config_file.exists():
            startup = Popen(
                ['python', 'startup.py', '655444:655448', '--rebuild'],
                cwd='./scripts/invokers'
            )
            startup.wait()
        with open(config_file) as config:
            self.config = json.load(config)
            self.config = {int(port): id_ for port, id_ in self.config['remote'].items()}

        self.status: dict[int, Status] = {}
        self.queue = Queue()
        for port in self.config:
            self.status[port] = Status.FREE
            self.queue.put(port)

        self.docker_client = docker.client.from_env()

    def acquire(self) -> SocketWrapper:
        port = self.queue.get()
        self.status[port] = Status.BUSY
        return SocketWrapper(port, self.config[port], self)

    def release(self, port: int):
        cnt = self.docker_client.containers.get(self.config[port])
        if cnt.status != 'running':
            logging.getLogger('invoker-pool').warning(f'Container on port {port} failed')
            raise FailedContainerException(cnt.logs())
        self.status[port] = Status.FREE
        self.queue.put(port)


INVOKER_POOL = InvokerPool()
