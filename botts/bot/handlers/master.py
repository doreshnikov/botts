import asyncio
import sys

import emoji
from aiogram import Bot, flags, Router
from aiogram.exceptions import TelegramBadRequest, TelegramAPIError
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.keyboard import InlineKeyboardBuilder

from botts.bot.util.text import escape_md
from botts.db.dao.master import Master
from botts.db.run import Run
from botts.db.util.filter import DBFilter
from botts.testsys.components.check.checker import Result, Verdict
from botts.testsys.components.test.event import Event
from botts.testsys.components.test.runner import Runner

master_router = Router()

PAGE_SIZE = 8


class MasterState(StatesGroup):
    RUNS_LIST = State()
    ACTION = State()
    FILTER = State()
    REJUDGE = State()
    JUDGING = State()
    RUN = State()


class RunCallback(CallbackData, prefix='run'):
    run_id: int


class FilterCallback(CallbackData, prefix='run_filter'):
    action: str


class ActionCallback(CallbackData, prefix='run_action'):
    action: str


class RejudgeCallback(CallbackData, prefix='run_rejudge'):
    confirm: bool


def run_selector(runs: list[Run], prev_page: bool, next_page: bool, middle_text: str):
    builder = InlineKeyboardBuilder()
    for run in runs:
        builder.row(InlineKeyboardButton(
            text=f'[{run.id_}] {run.task_id} - {run.verdict}',
            callback_data=RunCallback(run_id=run.id_).pack()
        ))
    builder.row(
        InlineKeyboardButton(
            text='<' if prev_page else emoji.emojize(':white_small_square:'),
            callback_data=FilterCallback(action='prev').pack()
        ),
        InlineKeyboardButton(
            text=middle_text,
            callback_data=FilterCallback(action='action').pack()
        ),
        InlineKeyboardButton(
            text='>' if next_page else emoji.emojize(':white_small_square:'),
            callback_data=FilterCallback(action='next').pack()
        )
    )
    return builder.as_markup()


@master_router.message(Command('runs'))
@flags.admin(True)
async def handle_runs(message: Message, state: FSMContext):
    runs_count = Master.runs_count()
    runs = Master.runs(PAGE_SIZE, 0)
    await state.update_data({
        'runs_count': runs_count,
        'runs': runs,
        'page': 0,
        'run_filters': []
    })
    runs_message = await message.reply('*All runs*:', reply_markup=run_selector(
        runs, False, runs_count > PAGE_SIZE,
        f'1-{min(PAGE_SIZE, runs_count)}/{runs_count}',
    ), parse_mode='Markdown')
    await state.update_data({'runs_message': runs_message})
    await state.set_state(MasterState.RUNS_LIST)


async def edit_runs(message: Message, state: FSMContext, page: int, filters: list[DBFilter]):
    runs_count = Master.runs_count(*filters)
    page = min(page, runs_count // PAGE_SIZE)
    page = max(page, 0)
    runs = Master.runs(PAGE_SIZE, page * PAGE_SIZE, *filters)
    text = 'All runs' if len(filters) == 0 else 'Filtered runs'
    low = PAGE_SIZE * page + 1
    high = min(low + PAGE_SIZE - 1, runs_count)
    await message.edit_text(f'*{text}*:', reply_markup=run_selector(
        runs, page > 0, page < runs_count // PAGE_SIZE,
        f'{low}-{high}/{runs_count}',
    ), parse_mode='Markdown')
    await state.update_data({
        'page': page,
        'runs': runs,
        'runs_count': runs_count
    })


@master_router.callback_query(FilterCallback.filter(), MasterState.RUNS_LIST)
async def handle_filter(query: CallbackQuery, state: FSMContext, bot: Bot):
    data = FilterCallback.unpack(query.data)
    state_data = await state.get_data()
    runs_message: Message = state_data['runs_message']
    page = state_data['page']
    filters = state_data['run_filters']

    if data.action == 'prev':
        return await edit_runs(runs_message, state, page - 1, filters)
    if data.action == 'next':
        return await edit_runs(runs_message, state, page + 1, filters)

    await query.answer('Выберите действие')
    action_message = await bot.send_message(
        query.from_user.id,
        'Выберите действие',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=action, callback_data=ActionCallback(action=action).pack())
            for action in ['filter', 'rejudge', 'cancel']
        ]]),
        parse_mode='Markdown'
    )
    await state.update_data({'action_message': action_message})
    await state.set_state(MasterState.ACTION)


@master_router.callback_query(ActionCallback.filter(), MasterState.ACTION)
async def handle_action(query: CallbackQuery, state: FSMContext, bot: Bot):
    data = ActionCallback.unpack(query.data)
    state_data = await state.get_data()
    action = data.action
    action_message: Message = state_data['action_message']

    if action == 'cancel':
        await action_message.delete()
        await state.set_state(MasterState.RUNS_LIST)
        return
    if action == 'filter':
        await action_message.edit_text(
            '*Текущие фильтры*:\n' + '\n'.join([
                f' · `{filter_}`' for filter_ in state_data['run_filters']
            ]) + '\nУкажите новые фильтры в том же формате',
            reply_markup=None,
            parse_mode='Markdown'
        )
        await state.set_state(MasterState.FILTER)
        return

    # action 'rejudge'
    await state.update_data({'selected_runs': Master.runs(
        None, 0, *state_data['run_filters']
    )})
    await action_message.edit_text(
        f'Перетестировать {state_data["runs_count"]} выбранных посылок?',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Да', callback_data=RejudgeCallback(confirm=True).pack()),
            InlineKeyboardButton(text='Нет', callback_data=RejudgeCallback(confirm=False).pack()),
        ]])
    )


@master_router.message(MasterState.FILTER)
async def handle_filter(message: Message, state: FSMContext):
    state_data = await state.get_data()
    runs_message: Message = state_data['runs_message']
    action_message: Message = state_data['action_message']
    new_filters = list(filter(
        lambda item: item is not None,
        [DBFilter.parse(line) for line in message.text.split('\n')]
    ))
    await state.update_data({'run_filters': new_filters})
    await action_message.delete()
    await state.set_state(MasterState.RUNS_LIST)
    await edit_runs(runs_message, state, 0, new_filters)


@master_router.callback_query(RejudgeCallback.filter(), MasterState.ACTION)
async def handle_rejudge(query: CallbackQuery, state: FSMContext, bot: Bot):
    data = RejudgeCallback.unpack(query.data)
    state_data = await state.get_data()
    runs_message: Message = state_data['runs_message']
    action_message: Message = state_data['action_message']

    if not data.confirm:
        await action_message.delete()
        await state.set_state(MasterState.RUNS_LIST)

    await action_message.edit_reply_markup(reply_markup=None)
    await runs_message.delete()
    selected_runs = state_data['selected_runs']
    batch_size = max(len(selected_runs) // 10, 1)
    reply = await action_message.reply('Ok, тестируется...')
    offset = 0
    old_count, new_count = 0, 0
    chat_action = ChatActionSender.typing(bot=bot, chat_id=action_message.from_user.id)
    await chat_action.__aenter__()

    def build_response(header: str, results: dict[int, Result]) -> str:
        nonlocal new_count

        def run_status(run: Run, result: Result):
            bullet = emoji.emojize(':small_blue_diamond:') if result.verdict == Verdict.OK \
                else emoji.emojize(':small_orange_diamond:')
            text = f'{bullet} \\[{run.id_}] _{run.task_id}_: `{result.verdict.name}`'
            if result.cause is not None:
                text += f', {escape_md(result.cause)}'
            return text

        run_data = [run for run in selected_runs if run.id_ in results]
        new_count = len(run_data) - offset
        return f'*{header}*\n' + '\n'.join([
            run_status(run, results[run.id_])
            for run in run_data[offset:]
        ])

    async def callback(testing_results: dict[int, Result]):
        nonlocal reply, new_count, old_count, offset
        if (len(selected_runs) - len(testing_results)) % batch_size == 0:
            try:
                text = build_response('Результаты', testing_results)
                await reply.edit_text(text, parse_mode='Markdown')
                old_count = new_count
            except TelegramBadRequest:
                offset = old_count
                text = build_response('Результаты', testing_results)
                reply = await bot.send_message(query.from_user.id, text, parse_mode='Markdown')
                old_count = new_count

    async def final_callback(testing_results: dict[int, Result]):
        nonlocal reply, new_count, old_count, offset
        try:
            text = build_response('Итог', testing_results)
            await reply.edit_text(text, parse_mode='Markdown')
        except TelegramBadRequest:
            offset = old_count
            text = build_response('Итог', testing_results)
            reply = await bot.send_message(query.from_user.id, text, parse_mode='Markdown')
        await chat_action.__aexit__(*sys.exc_info())
        await state.clear()

    await state.set_state(MasterState.JUDGING)
    loop = asyncio.get_running_loop()
    loop.create_task(Runner.rejudge(
        selected_runs, Event.resolve_task,
        callback, final_callback
    ))

    await state.clear()
