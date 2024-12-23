import asyncio
import json
import sys
import time
from io import BytesIO

import emoji
from aiogram import Bot, F, flags, Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.keyboard import InlineKeyboardBuilder

from botts.bot.config.local import ADMIN_ID, report_event
from botts.bot.util.text import escape_md
from botts.db import database
from botts.db.dao.students import Students
from botts.db.run import Run
from botts.db.student import Student
from botts.db.submission import Submission
from botts.testsys.components.base.task import Task
from botts.testsys.components.check.checker import Result, Verdict
from botts.testsys.components.extract.jupyter import NotebookContainer
from botts.testsys.components.test.event import Event

grade_router = Router()


class GradeState(StatesGroup):
    INITIAL = State()
    EVENT_SELECT = State()
    FORMAT_SELECT = State()
    CODE = State()
    FILE = State()
    TESTING = State()
    STATUS = State()


class EventCallback(CallbackData, prefix='event'):
    option: str


class FormatCallback(CallbackData, prefix='format'):
    option: str


def event_selector(allow_expired: bool = True):
    builder = InlineKeyboardBuilder()
    count = 0
    for event_id, event in Event.ALL.items():
        if event.is_expired and not allow_expired:
            continue
        count += 1
        builder.row(
            InlineKeyboardButton(
                text=f'{event.name} (до {event.deadline.day:02d}.{event.deadline.month:02d})',
                callback_data=EventCallback(option=event_id).pack()
            )
        )
    if count == 0:
        return None
    builder.adjust(*(1 for _ in range(count)))
    return builder.as_markup()


def format_selector():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='.ipynb file', callback_data=FormatCallback(option='ipynb').pack()),
        InlineKeyboardButton(text='separate messages', callback_data=FormatCallback(option='text').pack())
    ]])


@grade_router.message(Command('grade'))
@flags.authorized(True)
async def handle_grade(message: Message, state: FSMContext):
    await state.set_state(GradeState.EVENT_SELECT)
    allow_expired = message.from_user.id == ADMIN_ID
    reply_markup = event_selector(allow_expired=allow_expired)
    text = (
        'Выберите контест, решения которого вы хотите отправить на проверку'
        if reply_markup is not None
        else 'Нет контестов, доступных для проверки'
    )
    reply = await message.reply(text, reply_markup=reply_markup)
    await state.update_data({'selector_message': reply})


@grade_router.callback_query(EventCallback.filter(), GradeState.EVENT_SELECT)
async def handle_event(query: CallbackQuery, state: FSMContext):
    data = EventCallback.unpack(query.data)
    allow_expired = query.from_user.id == ADMIN_ID
    selector_message: Message = (await state.get_data())['selector_message']
    if Event.ALL[data.option].is_expired and not allow_expired:
        await query.answer('Дедлайн по этому заданию уже прошел')
        return

    await state.update_data({'event_id': data.option})
    await state.set_state(GradeState.FORMAT_SELECT)
    await query.answer('Ok!')
    await selector_message.edit_text(
        'Выберите формат сдачи \\(`.ipynb` или отдельным сообщением с кодом по конкретной задаче\\)',
        reply_markup=format_selector(),
        parse_mode='MarkdownV2'
    )


@grade_router.callback_query(FormatCallback.filter(), GradeState.FORMAT_SELECT)
async def handle_format(query: CallbackQuery, state: FSMContext, _student: Student):
    data = FormatCallback.unpack(query.data)
    state_data = await state.get_data()
    selector_message: Message = state_data['selector_message']
    await query.answer('Ok!')

    if data.option == 'text':
        await state.set_state(GradeState.CODE)
        await selector_message.edit_text(
            f'Для сдачи задания \'{state_data["event_id"]}\' следующим сообщением '
            f'пришлите код решения какой-либо задачи следующим сообщением',
            reply_markup=None,
            parse_mode='Markdown'
        )
    else:
        await state.set_state(GradeState.FILE)
        await selector_message.edit_text(
            f'Для сдачи задания \'{state_data["event_id"]}\' пришлите `.ipynb`-файл '
            f'со всеми выполненными вами заданиями',
            reply_markup=None,
            parse_mode='Markdown'
        )


async def _get_author(message: Message, _student: Student) -> Student:
    is_admin = message.from_user.id == ADMIN_ID
    submission_author = _student
    if (author := message.forward_from) is not None:
        if is_admin:
            submission_author = Students.get_student_by_tg_id(author.id)
            if submission_author is None:
                await message.reply('Изначальный отправитель не числится среди студентов курса')
            await message.reply(f'Автор: {submission_author.name}')
        else:
            await report_event(f'User {message.from_user.id} submitted a file authored by {author.id}')
    return submission_author


async def _grade(
        author: Student, container: NotebookContainer, file_path: str | None,
        message: Message, state: FSMContext, bot: Bot
):
    event_id = (await state.get_data())['event_id']
    event = Event.ALL[event_id]
    batch_size = max(len(event.tasks) // 10, 1)
    reply = await message.reply('Ok, тестируется...')
    chat_action = ChatActionSender.typing(bot=bot, chat_id=message.from_user.id)
    await chat_action.__aenter__()

    def build_response(header: str, results: dict[str, Result]) -> str:
        def task_status(task: Task, result: Result):
            bullet = emoji.emojize(':small_blue_diamond:') if result.verdict == Verdict.OK \
                else emoji.emojize(':small_orange_diamond:')
            text = f'{bullet} _{task.id_}_: `{result.verdict.name}`'
            if result.verdict != Verdict.OK:
                text += f' ({result.verdict.value})'
            if result.cause is not None:
                text += f', {escape_md(result.cause)}'
            return text

        return f'*{header}*\n' + '\n'.join([
            task_status(task, results[task.id_])
            for task in event.tasks
            if task.id_ in results
        ])

    async def callback(testing_results: dict[str, Result]):
        if (len(testing_results) - len(event.tasks)) % batch_size == 0:
            try:
                text = build_response('Результаты', testing_results)
                await reply.edit_text(text, parse_mode='Markdown')
            except TelegramBadRequest | TelegramAPIError:
                pass

    async def final_callback(testing_results: dict[str, Result]):
        text = build_response('Итог', testing_results)
        await reply.edit_text(text, parse_mode='Markdown')
        await chat_action.__aexit__(*sys.exc_info())
        await state.clear()

    await state.set_state(GradeState.TESTING)
    submission = Submission.create(
        timestamp=time.time(),
        event=event_id,
        student=author,
        file_path=file_path,
        message_id=reply.message_id
    )
    loop = asyncio.get_running_loop()
    loop.create_task(Event.ALL[event_id].run(
        container, submission,
        callback, final_callback
    ))


@grade_router.message(GradeState.CODE)
async def handle_code(message: Message, state: FSMContext, bot: Bot, _student: Student):
    author = await _get_author(message, _student)
    container = NotebookContainer({
        'cells': [
            {
                'cell_type': 'code',
                'source': [message.text]
            }
        ]
    })
    await _grade(author, container, None, message, state, bot)


@grade_router.message(GradeState.FILE, F.content_type == 'document')
async def handle_file(message: Message, state: FSMContext, bot: Bot, _student: Student):
    author = await _get_author(message, _student)

    document = message.document
    if not document.file_name.endswith('.ipynb'):
        await message.reply('Ожидается файл с разрешением .ipynb')
        return

    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        file_content = BytesIO()
        file = await bot.get_file(document.file_id)
        await bot.download_file(file.file_path, destination=file_content)
        file_content.seek(0)

    try:
        json_content = json.load(file_content)
        container = NotebookContainer(json_content)
    except json.JSONDecodeError as e:
        await message.reply(f'Файл поврежден или не является корректным .ipynb-файлом:\n```{e}```')
        return
    except ValueError as e:
        await message.reply(f'Файл не является корректным .ipynb-файлом:\n```{e}```')
        return

    await _grade(author, container, file.file_path, message, state, bot)


@grade_router.message(Command('status'))
@flags.authorized(True)
async def handle_status(message: Message, state: FSMContext):
    await state.set_state(GradeState.STATUS)
    reply = await message.reply(
        'Выберите задание, по которому хотите узнать статус',
        reply_markup=event_selector()
    )
    await state.update_data({'selector_message': reply})


@grade_router.callback_query(EventCallback.filter(), GradeState.STATUS)
async def handle_event_status(query: CallbackQuery, state: FSMContext, _student: Student):
    data = EventCallback.unpack(query.data)
    selector_message: Message = (await state.get_data())['selector_message']
    event_id = data.option
    event = Event.ALL[event_id]

    submissions = (Submission
                   .select(Submission)
                   .join(Student)
                   .where((Student.id_ == _student.id_) & (Submission.event == event_id)))
    submission_ids = submissions.select(Submission.id_)
    await query.answer('Ok!')

    def task_status(task: Task):
        runs = (Run
                .select(Run)
                .join(Submission)
                .where(Submission.id_.in_(submission_ids) & (Run.task_id == task.id_))
                .order_by(Submission.timestamp)).execute()
        verdicts = []
        for run in runs:
            if run.verdict == Verdict.OK.name:
                return emoji.emojize(':small_blue_diamond:') + f' _{task.id_}_: `OK`'
            verdicts.append(f'`{run.verdict}`')
        return emoji.emojize(':small_orange_diamond:') + f' _{task.id_}_: ' + ', '.join(verdicts)

    await selector_message.edit_text(
        f'*Статус по задачам* {event_id}:\n' + '\n'.join([
            task_status(task)
            for task in event.tasks
        ]),
        parse_mode='Markdown'
    )
    await state.clear()


@grade_router.message(Command('compression_rate'))
@flags.authorized(True)
async def handle_compression_rate(message: Message, _student: Student):
    cursor = database.execute_sql(
        'select rate from compression_rate where student_id = ?',
        (_student.id_,)
    ).fetchall()
    if len(cursor) == 0:
        await message.reply('Вы еще не решили задание _3-encode-decode_', parse_mode='Markdown')
    else:
        await message.reply(f'Ваш compression rate в _3-encode-decode_ равен {cursor[0][0]}', parse_mode='Markdown')
