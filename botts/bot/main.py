import asyncio

from aiogram import Dispatcher

from tgutils.middleware.logging import LoggingMiddleware, DEFAULT_FIELD_RULES

from common.logging import setup_logging
from .config.local import BOT

from .handlers.grade import grade_router
from .handlers.infra.register import router as register_router
from .handlers.infra.start import router as start_router
from .handlers.master import master_router
from .handlers.statement import statement_router

from .middlewares.testing_wall import TestingWall
from .middlewares.tg_user_data import AuthorizationMiddleware, StudentDataMiddleware

dispatcher = Dispatcher()
dispatcher.include_routers(
    start_router,
    register_router,
    grade_router,
    statement_router
)
dispatcher.include_router(master_router)

dispatcher.update.outer_middleware(LoggingMiddleware(field_rules=DEFAULT_FIELD_RULES))
dispatcher.update.outer_middleware(StudentDataMiddleware())
dispatcher.message.middleware(AuthorizationMiddleware())
dispatcher.message.middleware(TestingWall())


async def main():
    import botts.testsys.config.contests.y2024.c00_introduction as intro
    _ = intro.EVENT
    await dispatcher.start_polling(BOT)


while True:
    setup_logging()
    asyncio.run(main())
