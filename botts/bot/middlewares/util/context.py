from typing import Any

from aiogram.types import TelegramObject


def extract_user_data(tg_object: TelegramObject) -> dict[str, Any] | None:
    data = tg_object.model_dump()
    if 'from_user' in data:
        return data['from_user']
    for key, value in data.items():
        if isinstance(value, dict) and 'from_user' in value:
            return value['from_user']
    return None
