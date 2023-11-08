import os
import tomllib

from aiogram import Bot

with open('config.toml', 'rb') as conf:
    config = tomllib.load(conf)
DEBUG_MODE = os.getenv('DEBUG', False)

COURSE_TABLE_URL = config['sheets']['course_table_url']

BOT_TOKEN = config['bot']['token']
DEBUG_BOT_TOKEN = config['bot']['debug_token']
ADMIN_ID = config['bot']['admin_id']

BOT = Bot(BOT_TOKEN if not DEBUG_MODE else DEBUG_BOT_TOKEN)


async def report_fail(logs: str):
    await BOT.send_message(ADMIN_ID, logs[-min(len(logs), 1000):], parse_mode='Markdown')


async def report_event(msg: str):
    await BOT.send_message(ADMIN_ID, msg, parse_mode='Markdown')
