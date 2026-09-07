import os 
from dotenv import load_dotenv

from vkbottle.bot import Bot as VKBot

from aiogram import Bot as TgBot, Dispatcher as TgDispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from classes.middleware import AlbumMiddleware
from maxapi import Dispatcher as MxDispatcher, Bot as MxBot


load_dotenv()

vk_usrs = {}
tg_usrs = {}
mx_usrs = {}

usrs = [vk_usrs, tg_usrs, mx_usrs]
mes = ["vk", "tg", "mx"]

VK_TOKEN = os.getenv("token")
vk_bot = VKBot(token=VK_TOKEN)

TG_TOKEN = os.getenv("tg_token")
URL = "socks5://" + os.getenv("prox")
dp = TgDispatcher()
dp.message.middleware(AlbumMiddleware())
session = AiohttpSession(proxy=URL)
tg_bot = TgBot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)

MX_TOKEN = os.getenv("max_token")
mx_bot = MxBot(MX_TOKEN)
mx_dp = MxDispatcher(mx_bot)

max_keyboards_len = 8
secret_len = 20
