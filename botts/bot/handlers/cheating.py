import json
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
from botts.db.dao.master import Master, Cheating
from botts.db.dao.students import Students
from botts.db.submission import Submission
from botts.db.run import Run
from botts.db.student import Student
from botts.db.util.filter import DBFilter
from botts.testsys.components.check.checker import Result, Verdict
from botts.testsys.components.test.event import Event
from botts.testsys.components.test.runner import Runner

cheating_router = Router()

PAGE_SIZE = 8


class CheatingState(StatesGroup):
    MENU = State()
    STUDENT = State()
    SECOND_STUDENT = State()
    STUDENT_MATCHES_LIST = State()
    EVENT = State()
    TASK = State()
    TASK_GROUPS_LIST = State()
    RUN = State()
    DUPLICATE_RUNS_LIST = State()


class MenuCallback(CallbackData, prefix='cheating_menu'):
    option: str


class EventCallback(CallbackData, prefix='cheating_event'):
    event_id: str
    

class SecondStudentCallback(CallbackData, prefix='cheating_second_student'):
    student_id: int
    

class RunCallback(CallbackData, prefix='cheating_run'):
    run_id: int
    

class TaskCallback(CallbackData, prefix='cheating_task'):
    task_id: str
    

class GroupCallback(CallbackData, prefix='cheating_group'):
    group_no: int


@cheating_router.message(Command('cheating'))
@flags.teacher(True)
async def handle_cheating(message: Message, state: FSMContext):
    menu_message = await message.reply('Search criteria',reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Pairs by student', callback_data=MenuCallback(option='student').pack())],
            [InlineKeyboardButton(text='Groups by task', callback_data=MenuCallback(option='task').pack())],
            [InlineKeyboardButton(text='Students by run id', callback_data=MenuCallback(option='run').pack())]
        ]
    ))
    await state.update_data({
        'message': menu_message
    })
    await state.set_state(CheatingState.MENU)
    

@cheating_router.callback_query(MenuCallback.filter(), CheatingState.MENU)
async def handle_option(query: CallbackQuery, state: FSMContext):
    option = MenuCallback.unpack(query.data).option
    message: Message = (await state.get_data())['message']
    if option == 'student':
        await message.edit_text('Type student\'s full name or its prefix', reply_markup=None)
        await state.set_state(CheatingState.STUDENT)
    elif option == 'task':
        await message.edit_text('Select event', reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=event.name, callback_data=EventCallback(event_id=event.id_).pack())]
                for _, event in Event.ALL.items()
            ]
        ))
        await state.set_state(CheatingState.EVENT)
    else:
        await message.edit_text('Send run id', reply_markup=None)
        await state.set_state(CheatingState.RUN)
        

@cheating_router.message(CheatingState.STUDENT)
async def handle_student(message: Message, state: FSMContext):
    name = message.text.strip()
    await message.delete()
    message: Message = (await state.get_data())['message']
    students = Students.get_students_starting_with(name)
    
    if len(students) == 0:
        await message.edit_text(f'No students starting with \'{name}\', try again')
        return
    if len(students) > 1:
        await message.edit_text(f'Multiple students starting with \'{name}\', try typing full name')
        return
    
    student = students[0]
    matches = Cheating.student_matches(student.id_)
    matches_list = list(matches.items())
    matches_list.sort(key=lambda pair: -len(pair[1]))
    matches_list = matches_list[:15]
    
    await state.update_data({
        'student': student,
        'matches': matches,
        'matches_list': matches_list
    })
    await message.edit_text(f'Student: {student.name}\nSelect second student', reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'{len(task_ids)} matches: {s[1]}', callback_data=SecondStudentCallback(student_id=s[0]).pack())]
            for s, task_ids in matches_list
        ]
    ))
    await state.set_state(CheatingState.SECOND_STUDENT)
    

@cheating_router.callback_query(SecondStudentCallback.filter(), CheatingState.SECOND_STUDENT)
async def handle_second_student(query: CallbackQuery, state: FSMContext):
    s_id = SecondStudentCallback.unpack(query.data).student_id
    data = await state.get_data()
    message: Message = data['message']
    
    student1: Student = data['student']
    student2: Student = Student.get_by_id(s_id)
    await state.update_data({
        'student2': student2
    })
    matches = data['matches'][(s_id, student2.name)]
    
    await message.edit_text(
        f'Student 1: {student1.name}\n'
        f'Student 2: {student2.name}\n',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=m[1], callback_data=RunCallback(run_id=m[0]).pack())]
                for m in matches[:15]
            ] + [
                [InlineKeyboardButton(text='Back', callback_data=RunCallback(run_id=-1).pack())]
            ]
        )
    )
    await state.set_state(CheatingState.STUDENT_MATCHES_LIST)
    
    
async def send_run(bot: Bot, user_id: int, student: Student, submission: Submission, run: Run):
    await bot.send_message(
        user_id,
        f'*Run {run.id_}*\n'
        f'Task: _{escape_md(run.task_id)}_\n'
        f'Student: {escape_md(student.name)}\n'
        f'Time: {escape_md(str(submission.timestamp))}\n'
        f'```python\n'
        f'{run.solution_source}\n'
        f'```',
        parse_mode='MarkdownV2'
    )


@cheating_router.callback_query(RunCallback.filter(), CheatingState.STUDENT_MATCHES_LIST)
async def handle_match(query: CallbackQuery, state: FSMContext, bot: Bot):
    r_id = RunCallback.unpack(query.data).run_id
    data = await state.get_data()
    student1: Student = data['student']
    student2: Student = data['student2']
    
    if r_id == -1:
        matches_list = data['matches_list']
        message = data['message']
        await message.edit_text(f'Student: {student1.name}\nSelect second student', reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f'{len(task_ids)} matches: {s[1]}', callback_data=SecondStudentCallback(student_id=s[0]).pack())]
                for s, task_ids in matches_list[:15]
            ]
        ))
        await state.set_state(CheatingState.SECOND_STUDENT)
        return
    
    run2: Run = Run.get_by_id(r_id)
    run1 = Cheating.get_run_by_hash(student1.id_, run2.task_id, run2.solution_hash)
    
    sub1 = Submission.get_by_id(run1.submission_id)
    await send_run(bot, query.from_user.id, student1, sub1, run1)
    sub2 = Submission.get_by_id(run2.submission_id)
    await send_run(bot, query.from_user.id, student2, sub2, run2)
    

@cheating_router.callback_query(EventCallback.filter(), CheatingState.EVENT)
async def handle_event(query: CallbackQuery, state: FSMContext):
    event_id = EventCallback.unpack(query.data).event_id
    data = await state.get_data()
    message: Message = data['message']
    
    event = Event.ALL[event_id]
    await state.update_data({
        'event': event
    })
    await message.edit_text(f'Event \'{event.name}\'. Select task', reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=task.id_, callback_data=TaskCallback(task_id=task.id_).pack())]
            for task in event.tasks
        ]
    ))
    await state.set_state(CheatingState.TASK)
    

@cheating_router.callback_query(TaskCallback.filter(), CheatingState.TASK)
async def handle_task(query: CallbackQuery, state: FSMContext, bot: Bot):
    task_id = TaskCallback.unpack(query.data).task_id
    data = await state.get_data()
    message: Message = data['message']
    
    groups = Cheating.task_groups(task_id)
    groups.sort(key=lambda g: -g[3])
    groups = groups[:15]
    
    await state.update_data({
        'task_id': task_id,
        'groups': groups
    })
    await message.edit_text(
        f'Found {len(groups)} groups. Send a student\'s name to filter',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f'Group {i + 1}: {g[3]} students', callback_data=GroupCallback(group_no=i).pack())]
            for i, g in enumerate(groups)
        ])
    )
    await state.set_state(CheatingState.TASK_GROUPS_LIST)
    

@cheating_router.message(CheatingState.TASK_GROUPS_LIST)
async def handle_student_filter(message: Message, state: FSMContext):
    name = message.text.strip()
    await message.delete()
    
    data = await state.get_data()
    message: Message = data['message']
    students = Students.get_students_starting_with(name)
    
    if len(students) == 0:
        await message.reply(f'No students starting with \'{name}\', try again')
        return
    if len(students) > 1:
        await message.reply(f'Multiple students starting with \'{name}\', try typing full name')
        return
    
    student = students[0]
    groups = data['groups']
    filtered_groups = [
        (i, g) for i, g in enumerate(groups)
        if student.id_ in list(map(int, g[1].split(',')))
    ]
    await message.edit_text(
        f'Found {len(filtered_groups)} groups with student \'{student.name}\'. Send another student\'s name to re-filter',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f'{g[3]} students', callback_data=GroupCallback(group_no=i).pack())]
            for i, g in filtered_groups
        ])
    )
    

@cheating_router.callback_query(GroupCallback.filter(), CheatingState.TASK_GROUPS_LIST)
async def handle_group(query: CallbackQuery, state: FSMContext, bot: Bot):
    group_no = GroupCallback.unpack(query.data).group_no
    data = await state.get_data()
    groups = data['groups']
    
    group = groups[group_no]
    run_ids = list(map(int, group[2].split(',')))
    students_used = set()
    
    for run in Run.select().where(Run.id_ << run_ids):
        sub = Submission.get_by_id(run.submission_id)
        student = Student.get_by_id(sub.student_id)
        if student.id_ in students_used:
            continue
        students_used.add(student.id_)
        await send_run(bot, query.from_user.id, student, sub, run)
        

@cheating_router.message(CheatingState.RUN)
async def handle_run_id(message: Message, state: FSMContext, bot: Bot):
    run_id = message.text
    from_user_id = message.from_user.id
    await message.delete()
    
    run: Run = Run.get_by_id(run_id)
    students_used = set()
    
    for run in Run.select().where(Run.solution_hash == run.solution_hash):
        sub = Submission.get_by_id(run.submission_id)
        student = Student.get_by_id(sub.student_id)
        if student.id_ in students_used:
            continue
        students_used.add(student.id_)
        await send_run(bot, from_user_id, student, sub, run)