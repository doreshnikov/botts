import logging
import os
from datetime import datetime

LOGLEVEL = os.getenv('LOGLEVEL', logging.DEBUG)


def setup_logging():
    now = datetime.now().strftime('%Y-%m-%d.%H-%M-%S')

    file_handler = logging.FileHandler(f'logs/{now}.log')
    file_handler.setLevel(LOGLEVEL)
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(LOGLEVEL)

    logging.basicConfig(
        level=LOGLEVEL,
        format=u'[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%d.%m.%y %H:%M:%S',
        force=True,
        handlers=[file_handler, stdout_handler],
        encoding='utf-8',
    )
