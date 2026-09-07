from classes.media import MediaType, Media, Sticker, StickerType
import subprocess
from config import secret_len
from functools import singledispatch
from maxapi.types.updates.message_created import MessageCreated
from aiogram.types import Message
from functools import wraps

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

async def check_secret(secret: str) -> bool:
    if len(secret) != secret_len*2+5:
        return False
    return True

async def createMedia(media_type: MediaType, filename: str, m_bytes:bytes) -> Media:
    return Media(
        media_type, filename, m_bytes
    )

async def createSticker(sticker_type: StickerType, filename: str, s_bytes: bytes) -> Sticker:
    return Sticker(
        sticker_type, filename, s_bytes
    )

def _extract_data_support(text):
    split_t = text.split(" ", maxsplit=2)         
    secret = None
    chat_name = None
    
    if len(split_t) > 1:
        secret = split_t[1]
    if len(split_t) > 2:
        chat_name = split_t[2]
    return (secret, chat_name)

@singledispatch
def _extract_data(el):
    raise f"Данный тип данных не поддерживается: {type(el)}"

@_extract_data.register(MessageCreated)
def _(event: MessageCreated, *args, **kwargs):
    split_t = _extract_data_support(event.message.body.text)
    return split_t

@_extract_data.register(Message)
def _(message: Message, *args, **kwargs):
    split_t = _extract_data_support(message.text)
    return split_t

def split_text(func):
    @wraps(func)
    async def wrapper(el, *args, **kwargs):
        secret, chat_name = _extract_data(el)
        return await func(el, secret, chat_name, *args, **kwargs)
        
    return wrapper
