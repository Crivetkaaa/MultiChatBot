from aiogram.types import Message
from functools import wraps


async def getFullName(message: Message) -> tuple[str, str]:
    usr_info = message.from_user
    last_name = usr_info.last_name or ""
    first_name = usr_info.first_name or ""
    full_name = f"{last_name} {first_name}".strip()

    if usr_info.username:
        url = f"https://t.me/{usr_info.username}"
    else:
        url = f"tg://user?id={usr_info.id}"

    return (full_name, url)

