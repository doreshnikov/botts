import ast
import sys
from multiprocessing import Process, Queue
from typing import Any

from .common import ChrootJail, InvokerServiceBase


class InvokerMP(InvokerServiceBase):
    @ChrootJail.jailed
    def run(self, source: ast.AST, args: tuple, time_limit: int, response: dict[str, Any]):
        fn_name = InvokerServiceBase._extract_function_name(source)

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
                queue.put({'verdict': 'RE', 'message': f'could not run: \'{e}\''})
                return
            try:
                value = eval(expr, globals(), locals())
                queue.put({'verdict': 'OK', 'value': value})
            except Exception as e:
                queue.put({'verdict': 'RE', 'message': f'runtime error \'{e}\''})

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


if __name__ == '__main__':
    port = int(sys.argv[1])
    InvokerMP(port).start()
