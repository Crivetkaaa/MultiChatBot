import os 
from dotenv import load_dotenv

from vkbottle.bot import Bot as VKBot

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


load_dotenv()

vk_usrs = {}
tg_usrs = {}

VK_TOKEN = os.getenv("token")
vk_bot = VKBot(token=VK_TOKEN)

TG_TOKEN = os.getenv("tg_token")
URL = "socks5://" + os.getenv("prox")
dp = Dispatcher()
session = AiohttpSession(proxy=URL)
tg_bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)


async def __init__():
    pass