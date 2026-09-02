import os 
from dotenv import load_dotenv

from vkbottle.bot import Bot as VKBot

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from classes.middleware import AlbumMiddleware


load_dotenv()

vk_usrs = {}
tg_usrs = {}

usrs = [vk_usrs, tg_usrs]
mes = ["vk", "tg"]

VK_TOKEN = os.getenv("token")
vk_bot = VKBot(token=VK_TOKEN)

TG_TOKEN = os.getenv("tg_token")
URL = "socks5://" + os.getenv("prox")
dp = Dispatcher()
dp.message.middleware(AlbumMiddleware())
session = AiohttpSession(proxy=URL)
tg_bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)
secret_len = 20
