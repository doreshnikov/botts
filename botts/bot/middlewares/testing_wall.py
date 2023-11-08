import json
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from botts.bot.handlers.grade import GradeState


class TestingWall(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data['state']
        if (await state.get_state()) == GradeState.TESTING:
            await event.reply('Дождитесь окончания тестирования')
            return
        return await handler(event, data)
