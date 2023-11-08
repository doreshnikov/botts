import logging

from aiogram import Bot, flags, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from botts.bot.config.local import COURSE_TABLE_URL
from botts.db.dao.students import Students
from botts.db.student import Student

register_router = Router()


class RegisterState(StatesGroup):
    INITIAL = State()
    NAME = State()
    SELECT = State()
    CONFIRM = State()


class NameCallback(CallbackData, prefix='name'):
    option_id: int


class ConfirmationCallback(CallbackData, prefix='confirm'):
    flag: bool


@register_router.message(Command('start'))
@register_router.message(Command('help'))
async def handle_start(message: Message):
    await message.reply(
        'Используйте команду /register, чтобы зарегистрироваться. '
        'После вам будут доступны команды из меню.'
    )


@register_router.message(Command('register'))
@flags.unauthorized(True)
async def handle_register(message: Message, state: FSMContext):
    await message.reply(
        'Напечатайте свою фамилию (с большой буквы).'
        f'\n(А еще лучше, просто скопируйте свои ФИО из [таблицы курса]({COURSE_TABLE_URL}))',
        parse_mode='Markdown'
    )
    await state.set_state(RegisterState.NAME)


@register_router.message(RegisterState.NAME)
async def handle_name(message: Message, state: FSMContext):
    name_prefix = message.text
    options = Students.get_students_starting_with(name_prefix)
    if len(options) == 0:
        await message.reply(
            'Не похоже, чтобы кто-то подходящий был в таблице'
            '\nУбедитесь в правильности написания, попробуйте '
            'скопировать себя из таблицы и попробовать еще раз.'
        )
        return
    elif len(options) == 1:
        student = options[0]
        await state.update_data({'student': student})
        await state.set_state(RegisterState.CONFIRM)
        confirmation_message = await message.reply(
            f'Это вы? *{student.name}* из группы *{student.group}*',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='Да', callback_data=ConfirmationCallback(flag=True).pack()),
                    InlineKeyboardButton(text='Нет', callback_data=ConfirmationCallback(flag=False).pack())
                ]
            ]),
            parse_mode='Markdown'
        )
        await state.update_data({'confirmation_message': confirmation_message})
    elif len(options) <= 5:
        names = [student.name for student in options]
        await state.update_data({'names': names})
        keyboard = [
            [InlineKeyboardButton(
                text=student.name,
                callback_data=NameCallback(option_id=i).pack()
            )]
            for i, student in enumerate(options)
        ]
        keyboard += [[InlineKeyboardButton(text='< Назад', callback_data=NameCallback(option_id=-1).pack())]]
        await state.set_state(RegisterState.SELECT)
        await message.reply(
            'Непонятно, вас таких больше одного... Выберите себя из списка:',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        await message.reply(
            'Мало информации, чтобы хотя бы приблизительно понять, кто вы. '
            'Попробуйте указать больше символов из своих ФИО.'
        )


@register_router.callback_query(NameCallback.filter(), RegisterState.SELECT)
async def handle_select(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = NameCallback.unpack(callback.data)
    if data.option_id == -1:
        await callback.answer('ОК, попробуйте указать свое имя еще раз')
        await state.set_state(RegisterState.NAME)
        return

    name = (await state.get_data())['names'][data.option_id]
    student = Student.get(Student.name == name)
    await state.update_data({'student': student})

    await callback.answer('ОК, осталось только подтвердить')
    confirmation_message = await bot.send_message(
        callback.from_user.id,
        f'Это вы? *{student.name}*',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Да', callback_data=ConfirmationCallback(flag=True).pack()),
                InlineKeyboardButton(text='Нет', callback_data=ConfirmationCallback(flag=False).pack())
            ]
        ]),
        parse_mode='Markdown'
    )
    await state.update_data({'confirmation_message': confirmation_message})
    await state.set_state(RegisterState.CONFIRM)


@register_router.callback_query(ConfirmationCallback.filter(), RegisterState.CONFIRM)
async def handle_confirmation(callback: CallbackQuery, state: FSMContext):
    data = ConfirmationCallback.unpack(callback.data)
    state_data = await state.get_data()
    if not data.flag:
        await callback.answer('ОК, напишите свои ФИО заново, чтобы точно выбрать верный вариант')
        await state.set_state(RegisterState.NAME)
        return

    student: Student = (await state.get_data())['student']
    from_user = callback.from_user
    if (tg_user := student.tg_user.first()) is None:
        Students.update_tg_data(student, from_user.id, from_user.username)
        await callback.answer('Супер!')
        await state.clear()
    else:
        mention = f'@{tg_user.username}' if tg_user.username is not None else tg_user.fullname
        confirmation_message: Message = state_data['confirmation_message']
        await callback.answer(f'Под этим именем уже зарегистрирован другой аккаунт ({mention}).\n'
                              f'Если это ошибка, обратитесь к @doreshnikov, иначе введите другие ФИО')
        await confirmation_message.delete()
        await state.set_state(RegisterState.NAME)
