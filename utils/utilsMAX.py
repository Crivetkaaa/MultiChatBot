from functools import wraps
from maxapi.types.updates.message_created import MessageCreated
from maxapi.types.updates.message_callback import MessageCallback



class Utils:
    @staticmethod
    def spliter(func):
        @wraps(func)
        async def wrapper(event: MessageCreated, *args, **kwargs):
            text = event.message.body.text
            split_t = text.split(" ", maxsplit=2)
            secret = None
            chat_name = None
            
            if len(split_t) > 1:
                secret = split_t[1]
            if len(split_t) > 2:
                chat_name = split_t[2]
            return await func(event, secret, chat_name, *args, **kwargs)
        return wrapper


    @staticmethod
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