import random
import io
from vkbottle import PhotoMessageUploader, DocMessagesUploader
from vkbottle.bot import Bot
import aiohttp
from classes.media import Media, MediaType, Sticker, StickerType
import asyncio
import vkbottle_types.objects as vt
import utils as Utils

class VkService:
    def __init__(self, vk_bot: Bot):
        self.bot = vk_bot
        self.doc_uploader = DocMessagesUploader(vk_bot.api)
        self.photo_uploader = PhotoMessageUploader(vk_bot.api)

    async def download_vk(self, url:str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()
        
    async def download_audio_vk(self, audio:vt.MessagesAudioMessage):
        return await self.download_vk(audio.link_ogg)
            
    async def download_photo_vk(self, photo:vt.PhotosPhoto):
        best_size = max(photo.sizes, key=lambda size: size.width)
        return await self.download_vk(best_size.url)

    async def download_doc_vk(self, doc:vt.DocsDoc):
        return await self.download_vk(doc.url)

    async def download_sticker_vk(self, sticker_id: int):
        url = f"https://vk.ru/sticker/1-{sticker_id}-352b"
        return await self.download_vk(url)

    async def send_vk(self, peer_id: int, text: str, attachment:str=None):
        try:
            await self.bot.api.messages.send(
                peer_id=peer_id,
                message=text,
                attachment=attachment, 
                random_id=random.randint(0, 2**31 - 1)
            )
        except Exception as e:
            print(f"Ошибка отправки в ВК: {e}")

    async def send_message(self, user_id:int, text:str):
        await self.send_vk(user_id, text)

    async def send_audio(self, user_id: int, audio: bytes, text:str):
        audio_buffer = io.BytesIO(audio)
        audio_buffer.name = "voice.ogg"

        attachment = await self.doc_uploader.upload(
            file_source=audio_buffer, 
            peer_id=user_id,
            type="audio_message" 
        )
        await self.send_vk(user_id, text, str(attachment))

    async def send_media(self, user_id: int, media: list[Media], text: str):
        media_at = await self.media_update(media, user_id)
        final_attachment = ",".join(media_at)
        await self.send_vk(user_id, text, final_attachment)

    async def media_update(self, media: list[Media], user_id: int):
        at = []
        if media:
            for item in media:
                data = io.BytesIO(item.m_bytes)
                data.name = item.filename
                if item.m_type == MediaType.PHOTO:
                    uploader = self.photo_uploader

                elif item.m_type == MediaType.DOCUMENT:
                    uploader = self.doc_uploader

                elif item.m_type == MediaType.VIDEO:
                    uploader = self.doc_uploader

                min_at = await uploader.upload(
                    file_source=data,
                    peer_id=user_id,
                    title=item.filename
                )
                at.append(min_at)
                await asyncio.sleep(0.3)
        return at

    async def sticker_update(self, user_id:int, sticker: Sticker, text:str):
        uploader = None
        if sticker.s_type == StickerType.PHOTO:
            uploader = self.photo_uploader
        elif sticker.s_type == StickerType.VIDEO:
            sticker.m_bytes = await Utils.webm_to_gif(sticker.m_bytes)
            uploader = self.doc_uploader

        data = io.BytesIO(sticker.m_bytes)
        data.name = sticker.filename

        at = await uploader.upload(
            file_source=data,
            peer_id=user_id,
            title=sticker.filename
        )

        finally_attachment = ",".join([at])
        await self.send_vk(user_id, text, finally_attachment)

    async def send_sticker(self, user_id:int, sticker: Sticker, text:str):
        await self.sticker_update(user_id, sticker, text)


    async def info_for_user(self, message_id, **params):
        if message_id:
            await self.bot.api.messages.edit(message_id=message_id, **params)
            return message_id
        msg = await self.bot.api.messages.send(**params)
        return msg