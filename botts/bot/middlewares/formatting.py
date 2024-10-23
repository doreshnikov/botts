from typing import Any, Awaitable, Callable, Dict

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message


_REPLACEMENTS = {
    '\xa0': ' '
}


class FormattingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        text = event.text
        for pattern, sub in _REPLACEMENTS.items():
            text = text.replace(pattern, sub)

        formatted_event = event.model_copy(update={
            'text': text
        })
        return await handler(formatted_event, data)
