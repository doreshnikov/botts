import ast
import os
import sys
import time

import process_isolation
from typing import Any

from .common import ChrootJail, InvokerServiceBase


class InvokerPI(InvokerServiceBase):
    SPINNER = 0.01

    def run(self, source: ast.AST, args: tuple, time_limit: int, response: dict[str, Any]):
        context = process_isolation.default_context()
        context.ensure_started()
        jail = ChrootJail()
        context.client.call(os.chroot, jail.directory)

        fn_name = InvokerServiceBase._extract_function_name(source)

        if not isinstance(source, ast.Module):
            source = ast.Module(body=[source])
        code = compile(source, filename='<ast>', mode='exec')
        evaluate = ast.parse(f'{fn_name}(*args)', mode='eval')
        expr = compile(evaluate, filename='<ast>', mode='eval')

        result = None
        try:
            context.client.call(exec, code)
        except Exception as e:
            result = {'verdict': 'RE', 'message': f'could not run: \'{e}\''}
        if result is None:
            try:
                value = process_isolation.byvalue(context.client.call(eval, expr))
                result = {'verdict': 'OK', 'value': value}
            except Exception as e:
                result = {'verdict': 'RE', 'message': f'runtime error \'{e}\''}

        time_passed = 0
        while context.client.state in [
            process_isolation.ClientState.READY,
            process_isolation.ClientState.WAITING_FOR_RESULT
        ] and time_passed <= time_limit:
            time_passed += InvokerPI.SPINNER
            time.sleep(InvokerPI.SPINNER)

        if time_passed > time_limit:
            context.client.terminate()
            self.logger.info('Solution timed out')
            response['verdict'] = 'TL'
            response['message'] = f'took more than {time_limit}s to complete'

        response.update(result)
        self.logger.info('Testing complete')


if __name__ == '__main__':
    port = int(sys.argv[1])
    InvokerPI(port).start()
