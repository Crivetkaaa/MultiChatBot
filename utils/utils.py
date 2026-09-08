from classes.media import MediaType, Media, Sticker, StickerType
import subprocess
from config import secret_len
from functools import singledispatch
from maxapi.types.updates.message_created import MessageCreated
from maxapi.types.updates.message_callback import MessageCallback
from aiogram.types import Message as TGMessage
from functools import wraps
from vkbottle.bot import Message, MessageEvent
from aiogram.types import CallbackQuery


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
def _(event: MessageCreated):
    split_t = _extract_data_support(event.message.body.text)
    return split_t

@_extract_data.register(TGMessage)
def _(message: TGMessage):
    split_t = _extract_data_support(message.text)
    return split_t

def split_text(func):
    @wraps(func)
    async def wrapper(el, *args, **kwargs):
        secret, chat_name = _extract_data(el)
        return await func(el, secret, chat_name, *args, **kwargs)
        
    return wrapper

@singledispatch
async def _getFullNameDispatch(el):
    raise f"Данный тип данных не поддерживается: {type(el)}"

@_getFullNameDispatch.register(MessageCreated | MessageCallback)
async def _(event:  MessageCreated | MessageCallback):
    usr_info = event.from_user

    last_name = usr_info.last_name or ""
    first_name = usr_info.first_name or ""

    full_name = f"{last_name} {first_name}".strip()

    if usr_info.username:
        url = f"https://max.ru/{usr_info.username}"
    else:
        url = f"https://max.ru/{usr_info.user_id}"
    return (full_name, url)

@_getFullNameDispatch.register(TGMessage|CallbackQuery)
async def _(message: TGMessage|CallbackQuery):
    usr_info = message.from_user
    last_name = usr_info.last_name or ""
    first_name = usr_info.first_name or ""
    full_name = f"{last_name} {first_name}".strip()
    if usr_info.username:
        url = f"https://t.me/{usr_info.username}"
    else:
        url = f"https://max.ru/{usr_info.user_id}"

    return (full_name, url)

@_getFullNameDispatch.register(Message|MessageEvent)
async def _(message: Message|MessageEvent):
    if type(message) == Message:
        usr_info = await message.get_user(fields=["screen_name"])
    else:
        user_info = await message.ctx_api.users.get(
        user_ids=[message.object.user_id], 
        fields=["screen_name"]
        )
        usr_info = user_info[0]
    full_name = usr_info.last_name + " " + usr_info.first_name
    if usr_info.screen_name:
        url = f"https://vk.ru/{usr_info.screen_name}"
    else:
        url = f"https://vk.ru/{message.user_id}"
    return (full_name, url)

async def getFullName(el):
    return await _getFullNameDispatch(el)