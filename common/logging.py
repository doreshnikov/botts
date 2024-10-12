import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%d.%m.%y %H:%M:%S",
        stream=sys.stdout,
        encoding='utf-8'
    )
