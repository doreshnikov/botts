from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command('start'))
@router.message(Command('help'))
async def handle_start(message: Message):
    await message.reply(
        'Используйте команду /register, чтобы зарегистрироваться. '
        'После вам будут доступны команды из меню.'
    )
