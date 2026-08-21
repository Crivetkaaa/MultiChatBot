from aiogram import Bot
from aiogram.types import BufferedInputFile
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from classes.media import Media, MediaType
from config import tg_bot

class TgService:
    def __init__(self, tg_bot:Bot):
        self.bot = tg_bot

    async def download_file_tg(self, file_id:str):
        file = await self.bot.get_file(file_id)
        file_in_memory = await self.bot.download_file(file.file_path)
        return file_in_memory.getvalue()

    async def send_message(self, user_id: int, text: str):
        await self.bot.send_message(user_id, text, parse_mode="HTML")

    async def send_audio(self, user_id: int, audio_raw: bytes, text:str):
        audio = BufferedInputFile(file=audio_raw, filename="audio.ogg")
        await self.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
        await self.bot.send_voice(chat_id=user_id, voice=audio)

    async def send_media(self, user_id: int, media: list[Media], text: str):
        media = await self.media_update(media, text)
        await self.bot.send_media_group(user_id, media)

    async def media_update(self, media: list[Media], text:str):
        m = []
        if media:
            first = True
            for i, item in enumerate(media):
                if item.m_type == MediaType.PHOTO:
                    Input = InputMediaPhoto
                elif item.m_type == MediaType.VIDEO:
                    Input = InputMediaVideo
                elif item.m_type == MediaType.DOCUMENT:
                    Input = InputMediaDocument 
                if first and item.m_type == MediaType.DOCUMENT:
                    caption_num = len(media)-1
                elif first and item.m_type != MediaType.DOCUMENT:
                    caption_num = 0
                m.append(
                    Input(
                        media=BufferedInputFile(
                            file=item.m_bytes, 
                            filename=item.filename
                        ), 
                        caption=text if i==caption_num else ""
                    )
                )

        return m

    async def info_for_user(self, user_id, text, keyboard=None):
        await self.bot.send_message(user_id, text, reply_markup=keyboard) 

tgService = TgService(tg_bot)
