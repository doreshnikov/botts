from aiogram import flags, Router
from aiogram.filters import Command
from aiogram.types import Message

from botts.db.student import Student
from botts.db.cf_user import CFUser

contest_router = Router()


@contest_router.message(Command('contest'))
@flags.authorized(True)
async def handle_contest(message: Message, _student: Student):
    cf_user: CFUser = _student.cf_user.first()
    if cf_user is None:
        await message.reply(
            'Вы не зарегистрированы на контесты на Codeforces. '
            'Обратитесь к @doreshnikov за регистрацией.',
            parse_mode='Markdown'
        )
    else:
        await message.reply(
            f'Контесты проходят по [ссылке](https://itmophystech.contest.codeforces.com/contests)'
            f'\nВаши данные для входа: `{cf_user.username}`/`{cf_user.password}`'
            f'\n\nДля старта контеста надо сначала зарегистрироваться на *виртуальное участие*. '
            f'При регистрации указывайте подходящее время начала.',
            parse_mode='Markdown', disable_web_page_preview=True
        )
