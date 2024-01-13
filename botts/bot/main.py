import asyncio
import logging
import sys

from aiogram import Dispatcher

from .config.local import BOT
from .handlers.contest import contest_router
from .handlers.grade import grade_router
from .handlers.master import master_router
from .handlers.register import register_router
from .middlewares.testing_wall import TestingWall
from .middlewares.tg_user_data import AuthorizationMiddleware, StudentDataMiddleware

dispatcher = Dispatcher()
dispatcher.include_routers(register_router, contest_router, grade_router)
dispatcher.include_router(master_router)

dispatcher.update.outer_middleware(StudentDataMiddleware())
dispatcher.message.middleware(AuthorizationMiddleware())
dispatcher.message.middleware(TestingWall())


async def main():
    import botts.testsys.config.hw02 as hw02
    import botts.testsys.config.midterm as midterm
    import botts.testsys.config.contest02.var4 as contest02
    import botts.testsys.config.hw03 as hw03
    _ = hw02.HW02
    _ = midterm.MIDTERM
    _ = contest02.CONTEST02
    _ = hw03.HW03
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
