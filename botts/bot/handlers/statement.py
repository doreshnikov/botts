from aiogram import Router, flags
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from botts.bot.config.local import ADMIN_ID

from .grade import event_selector
from ..util.text import escape_md
from ...testsys.components.test.event import Event

statement_router = Router()


class EventCallback(CallbackData, prefix='event'):
    option: str


class StatementState(StatesGroup):
    INITIAL = State()
    EVENT_SELECT = State()


@statement_router.message(Command('statement'))
@flags.authorized(True)
async def handle_grade(message: Message, state: FSMContext):
    await state.set_state(StatementState.EVENT_SELECT)
    reply_markup = event_selector(allow_expired=message.from_user.id == ADMIN_ID)
    text = (
        'Выберите контест'
        if reply_markup is not None
        else 'Нет доступных контестов'
    )
    reply = await message.reply(text, reply_markup=reply_markup)
    await state.update_data({'selector_message': reply})


@statement_router.callback_query(EventCallback.filter(), StatementState.EVENT_SELECT)
async def handle_event(query: CallbackQuery, state: FSMContext):
    data = EventCallback.unpack(query.data)
    selector_message: Message = (await state.get_data())['selector_message']
    event = Event.ALL[data.option]

    await query.answer('Ok!')
    await state.clear()
    await selector_message.edit_text(
        event.render_statement(),
        reply_markup=None,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
