import json
from typing import Any, Awaitable, Callable, Dict

from aiogram.dispatcher.flags import get_flag
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message, TelegramObject

from botts.bot.config.local import ADMIN_ID
from botts.bot.middlewares.util.context import extract_user_data
from botts.db.dao.students import Students
from botts.db.student import Student


class StudentDataMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        from_user = extract_user_data(event)
        student = Students.get_student_by_tg_id(from_user['id'])
        if student:
            tg_data = student.tg_user.first()
            if tg_data.username != from_user['username']:
                tg_data.username = from_user['username']
                tg_data.save()
            data['_student'] = student
        return await handler(event, data)


class AuthorizationMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        student: Student = data.get('_student')
        if get_flag(data, 'unauthorized') and student:
            await event.reply(
                f'Вы зарегистрированы как *{student.name}* из группы *{student.group}*.'
                '\nЗа списком команд обратитесь в меню бота.',
                parse_mode='Markdown'
            )
            return False
        if get_flag(data, 'authorized') and not student:
            await event.reply(
                f'Вы не зарегистрированы. Используйте /register для регистрации, после чего вам '
                f'станут доступны другие команды.'
            )
            return False
        if get_flag(data, 'admin'):
            tg_id = student.tg_user.first().tg_id
            if tg_id != ADMIN_ID:
                return False
        return await handler(event, data)
