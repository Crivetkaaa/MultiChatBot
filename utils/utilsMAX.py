from maxapi.types.updates.message_created import MessageCreated
from maxapi.types.updates.message_callback import MessageCallback


async def getFullName(event: MessageCreated | MessageCallback) -> tuple[str, str]:
    usr_info = event.from_user

    last_name = usr_info.last_name or ""
    first_name = usr_info.first_name or ""

    full_name = f"{last_name} {first_name}".strip()

    if usr_info.username:
        url = f"https://max.ru/{usr_info.username}"
    else:
        url = f"max://user?id={usr_info.user_id}"

    return (full_name, url)