from dataclasses import dataclass, field

from aiogram import Bot, flags, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.formatting import Text, as_line, Url, TextLink, Bold, Italic

from botts.bot.config.local import COURSE_TABLE_URL, report_event
from botts.bot.util.text import escape_md
from botts.db.dao.students import Students
from botts.db.student import Student
from tgutils.consts.aliases import MAX_BUTTON_ROWS, KeyboardBuilder, Button
from tgutils.context import Context
from tgutils.context.types import Response

router = Router()


@dataclass
class RegisterContext(Context):
    name_prefix: str | None = None
    selection_fail: str | None = None
    suitable_options: list[Student] = field(default_factory=list)
    selected_student: Student | None = None


class RegisterState(StatesGroup):
    PREFIX = State()
    SELECT = State()
    CONFIRM = State()


@RegisterContext.register(RegisterState.PREFIX)
def register_menu(ctx: RegisterContext) -> Response:
    lines = [
        as_line('Напечатайте свою фамилию (с большой буквы)'),
        as_line(f'(А еще лучше, просто скопируйте свои ФИО из ', TextLink('таблицы курса', url=COURSE_TABLE_URL)),
    ]
    if ctx.selection_fail is not None:
        lines = [
            as_line(Italic(f'Запрос \'{ctx.name_prefix}\': {ctx.selection_fail}'), end='\n\n'),
            *lines
        ]

    ctx.selection_fail = None
    ctx.name_prefix = None

    return Response(
        text=Text(*lines),
        markup=KeyboardBuilder().row(ctx.menu_button(ctx.Action.FINISH)).as_markup()
    )


@router.message(Command('register'))
@flags.unauthorized(True)
@RegisterContext.entry_point
async def handle_register(ctx: RegisterContext, message: Message):
    await ctx.advance(RegisterState.PREFIX, message.reply, cause=message)


class OptionCallback(CallbackData, prefix='register-option'):
    option_id: int


@RegisterContext.register(RegisterState.SELECT)
def select_menu(ctx: RegisterContext) -> Response:
    keyboard = KeyboardBuilder()
    for i, student in enumerate(ctx.suitable_options):
        keyboard.row(Button(text=student.name, callback_data=OptionCallback(option_id=i).pack()))
    keyboard.row(ctx.menu_button(ctx.Action.BACK), ctx.menu_button(ctx.Action.FINISH))

    return Response(
        text='Выберите себя из списка',
        markup=keyboard.as_markup()
    )


@router.message(RegisterState.PREFIX)
@RegisterContext.inject
async def handle_name(ctx: RegisterContext, message: Message):
    ctx.name_prefix = message.text
    options = Students.get_students_starting_with(ctx.name_prefix)
    await message.delete()

    if len(options) == 0:
        ctx.selection_fail = 'пользователи не найдены'
        return await ctx.advance(RegisterState.PREFIX)
    if len(options) > MAX_BUTTON_ROWS - 1:
        ctx.selection_fail = 'слишком много вариантов, уточните запрос'
        return await ctx.advance(RegisterState.PREFIX)

    ctx.suitable_options = options
    if len(options) == 1:
        ctx.selected_student = options[0]
        return await ctx.advance(RegisterState.CONFIRM)

    await ctx.advance(RegisterState.SELECT)


class ConfirmCallback(CallbackData, prefix='register-confirm'):
    pass


@RegisterContext.register(RegisterState.CONFIRM)
def confirm_menu(ctx: RegisterContext) -> Response:
    keyboard = KeyboardBuilder()
    keyboard.row(Button(text='Подтвердить', callback_data=ConfirmCallback().pack()))
    keyboard.row(ctx.menu_button(ctx.Action.BACK), ctx.menu_button(ctx.Action.FINISH))

    return Response(
        text=Text('Вы \N{EN DASH} ', Bold(ctx.selected_student.name, '?')),
        markup=keyboard.as_markup()
    )


@router.callback_query(OptionCallback.filter(), RegisterState.SELECT)
@RegisterContext.inject
async def handle_select(ctx: RegisterContext, query: CallbackQuery):
    data = OptionCallback.unpack(query.data)
    ctx.selected_student = ctx.suitable_options[data.option_id]

    await query.answer('Ok!')
    await ctx.advance(RegisterState.CONFIRM)


@router.callback_query(ConfirmCallback.filter(), RegisterState.CONFIRM)
@RegisterContext.inject
async def handle_confirmation(ctx: RegisterContext, query: CallbackQuery):
    from_user = query.from_user
    student = ctx.selected_student

    if (tg_user := ctx.selected_student.tg_user.first()) is None:
        Students.update_tg_data(ctx.selected_student, from_user.id, from_user.username)
        if student.group == 'teacher':
            await report_event(f'User @{escape_md(from_user.username)} ({from_user.id}) registered as a teacher')
        await query.answer('Супер!')
        return await ctx.finish()

    await query.answer(f'Ошибка!')

    mention = f'@{tg_user.username}' if tg_user.username is not None else tg_user.fullname
    ctx.name_prefix = ctx.selected_student.name
    ctx.selection_fail = f'аккаунт уже занят пользователем ({mention}), обратитесь к администратору, если это ошибка'
    await ctx.backoff_until(RegisterState.PREFIX)


RegisterContext.prepare(router)
