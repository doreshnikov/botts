import ast
import os
import pickle
import subprocess
import sys
import time

from typing import Any

from .common import InvokerServiceBase

READER = '''
import pickle
import sys

args = pickle.load(sys.stdin, encoding='utf-8')
'''

WRITER = '''
pickle.dump(RESULT, sys.stdout, encoding='utf-8')
sys.stdout.flush()
'''


class InvokerISO(InvokerServiceBase):
    def run(self, source: ast.AST, args: tuple, time_limit: int, response: dict[str, Any]):
        os.system('isolate --init')

        fn_name = InvokerServiceBase._extract_function_name(source)
        text_source = ast.unparse(source)
        with open('/tmp/sol.py', 'w') as solution:
            solution.write('\n'.join([
                READER,
                text_source,
                f'value = {fn_name}(*args)',
                WRITER
            ]))

        try:
            process = subprocess.Popen([
                'isolate', '--run', 'python', '/tmp/solution.py',
                '--meta=/tmp/meta', f'--time={time_limit}', '--wall-time=10'
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            process.stdin.write(pickle.dumps(args, encoding='utf-8'))
            try:
                result = {'verdict': 'OK', 'value': pickle.loads(process.stdout.read())}
            except pickle.UnpicklingError as e:
                result = {'verdict': 'CF', 'message': f'Invalid data in output stream: \'{e}\''}
            exit_code = process.returncode
        except Exception as e:
            exit_code = None
            result = {'verdict': 'CF', 'message': f'failed to start process: \'{e}\''}

        if result['verdict'] != 'CF':
            if exit_code == 1:
                result = {'verdict': 'RE', 'message': 'TODO'}  # TODO parse meta file
            # TODO parse meta file for TL info
            if False:
                response['verdict'] = 'TL'
                response['message'] = f'took more than {time_limit}s to complete'

        response.update(result)
        os.system('isolate --cleanup')
        self.logger.info('Testing complete')


if __name__ == '__main__':
    port = int(sys.argv[1])
    InvokerISO(port).start()
