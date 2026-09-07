from maxapi import Bot
import aiohttp
from classes.media import Media
from maxapi.types.input_media import InputMediaBuffer

class MxService:
    def __init__(self, mx_bot:Bot):
        self.bot = mx_bot


    async def download_file(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as response:
                return await response.read()

        
    async def info_for_user(self, user_id, text, keyboard=None):
        await self.bot.send_message(
            user_id=user_id,
            text=text,
            attachments=[keyboard] if keyboard else None
        )

    async def send_message(self, user_id: int, text: str):
        await self.bot.send_message(user_id=user_id, text = text)

    async def send_media(
        self,
        user_id,
        media: list[Media],
        text: str | None = None
    ):
        send_media = []
        for m in media:
            send_media.append(InputMediaBuffer(
                m.m_bytes, m.filename
            ))
        await self.bot.send_message(user_id=user_id, text=text, attachments=send_media)

    async def send_sticker(self, user_id:int, sticker, text: str):
        await self.send_media(user_id, [sticker], text)
