from .media import MediaType, Media, Sticker, StickerType
from aiogram.types import Message as TGMessage
from vkbottle.bot import Message, MessageEvent
import subprocess
from functools import wraps
from config import secret_len

class Utils:
    @staticmethod
    async def webm_to_gif(m_bytes: bytes) -> bytes:
        result = subprocess.run(
        [
            "ffmpeg",
            "-i", "pipe:0",
            "-vf", "fps=15,scale=512:-1:flags=lanczos",
            "-f", "gif",
            "pipe:1"
        ],
            input=m_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        return result.stdout

    @staticmethod
    async def check_secret(secret: str) -> bool:
        if len(secret) != secret_len*2+5:
            return False
        return True

    @staticmethod
    async def createMedia(media_type: MediaType, filename: str, m_bytes:bytes) -> Media:
        return Media(
            media_type, filename, m_bytes
        )

    @staticmethod
    async def createSticker(sticker_type: StickerType, filename: str, s_bytes: bytes) -> Sticker:
        return Sticker(
            sticker_type, filename, s_bytes
        )

    @staticmethod
    async def getFullNameTg(message: TGMessage) -> tuple[str, str]:
        usr_info = message.from_user
        last_name = usr_info.last_name or ""
        first_name = usr_info.first_name or ""
        full_name = f"{last_name} {first_name}".strip()
    
        if usr_info.username:
            url = f"https://t.me/{usr_info.username}"
        else:
            url = f"tg://user?id={usr_info.id}"

        return (full_name, url)

    @staticmethod
    async def getFullNameVk(message: Message|MessageEvent) -> tuple[str, str]:
        if type(message) == Message:
            usr_info = await message.get_user(fields=["screen_name"])
        else:
            user_info = await message.ctx_api.users.get(
            user_ids=[message.object.user_id], 
            fields=["screen_name"]
            )
            usr_info = user_info[0]
        full_name = usr_info.last_name + " " + usr_info.first_name
        url = f"https://vk.ru/{usr_info.screen_name}"
        return (full_name, url)
    
    @staticmethod
    def split_text(func):
        @wraps(func)
        def wrapper(text, *args, **kwargs):
            split_t = text.text.split(" ", maxsplit=2)         
            if len(split_t) > 2:
                split_t = split_t[1:3]
            else:
                split_t = [split_t[-1]]
                
            return func(text, *split_t, *args, **kwargs)
            
        return wrapper
