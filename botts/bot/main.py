import asyncio
import logging
import sys

from aiogram import Dispatcher

from .config.local import BOT
from .handlers.contest import contest_router
from .handlers.grade import grade_router
from .handlers.master import master_router
from .handlers.register import register_router
from .handlers.statement import statement_router
from .middlewares.testing_wall import TestingWall
from .middlewares.tg_user_data import AuthorizationMiddleware, StudentDataMiddleware

dispatcher = Dispatcher()
dispatcher.include_routers(register_router, contest_router, grade_router, statement_router)
dispatcher.include_router(master_router)

dispatcher.update.outer_middleware(StudentDataMiddleware())
dispatcher.message.middleware(AuthorizationMiddleware())
dispatcher.message.middleware(TestingWall())


async def main():
    import botts.testsys.config.contests.y2024.c00_introduction as intro
    _ = intro.EVENT
    await dispatcher.start_polling(BOT)


while True:
    try:
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%d.%m.%y %H:%M:%S",
            stream=sys.stdout
        )
        asyncio.run(main())
    except Exception as e:
        print(e)
