from aiogram import Bot
from aiogram.types import BufferedInputFile
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaSticker
from classes.media import Media, MediaType, StickerType, Sticker
from utils.utils import Utils

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

    async def sticker_type(self, sticker: Sticker) -> Sticker:
        if sticker.s_type == StickerType.VIDEO:
            sticker.m_bytes = await Utils.webm_to_gif(sticker.m_bytes)
            sticker.filename = "sticker.gif"
        return sticker

    async def sticker_update(self, user_id:int, sticker: Sticker, text:str):
        sticker = await self.sticker_type(sticker)
        file = BufferedInputFile(
            file=sticker.m_bytes,
            filename=sticker.filename
        )

        if sticker.s_type == StickerType.PHOTO:
            await self.bot.send_photo(
                chat_id=user_id,
                photo=file,
                caption=text
            )

        elif sticker.s_type == StickerType.VIDEO:
            await self.bot.send_video(
                chat_id=user_id,
                video=file,
                caption=text
            )

    async def send_sticker(self, user_id: int, sticker:Sticker, text:str):
        await self.sticker_update(user_id, sticker, text)

    async def info_for_user(self, user_id, text, keyboard=None):
        await self.bot.send_message(user_id, text, reply_markup=keyboard) 
