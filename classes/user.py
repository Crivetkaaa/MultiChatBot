import secrets
import random
import base64
import aiohttp
import io, asyncio
from config import tg_usrs, vk_usrs
from database import db
from config import vk_bot, tg_bot
from aiogram.types import BufferedInputFile
from vkbottle import PhotoMessageUploader
from vkbottle import DocMessagesUploader
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from resours import texts
import vkbottle_types.objects as vt

photo_uploader = PhotoMessageUploader(vk_bot.api)
doc_uploader = DocMessagesUploader(vk_bot.api)


class User:
    def __init__(self, user_id, secret=None, mes=None):
        self.user_id = user_id
        self.secret = secret if secret is not None else self.generateSecret(mes)
        self.in_message = False
        self.who_secret = None
        self.head = None


    def generateSecret(self, mes: str, bytes: int = 32):
        mes_code = base64.b64encode(mes.encode("utf-8")).decode("utf-8")
        return mes_code + ":" + secrets.token_hex(bytes)

    async def create(self, mes: str):
        await db.createUser(mes, self.user_id, self.secret)


    async def generate_head(self, secret, name, url, from_):
        if "dms=" in secret:
            self.head = f"Сообщение из {from_}\nОт: {name}\nИз: {url}\n\n"
        elif "dGc=" in secret:
            self.head = f"Сообщение из {from_}\nОт: <a href=\"{url}\">{name}</a>\n\n"
        else:
            self.head = f"Сообщение из {from_}\nОт: {name}\n\n"

    async def finally_text(self, text: str) -> str:
        safe_text = text or ""
        return self.head + safe_text

    async def start_chat(self, secret:str, full_name:str, url:str, from_:str):
        await self.generate_head(secret, full_name, url, from_)
        self.in_message = True
        self.who_secret = secret

    async def end_chat(self):
        self.in_message = False
        self.who_secret = None
        self.head = None

    async def err_end_chat(self, text:str):
        await self.info_for_user(text)
        await self.end_chat()


    async def download_file_tg(self, file_id:str):
        file = await tg_bot.get_file(file_id)
        file_in_memory = await tg_bot.download_file(file.file_path)
        return file_in_memory.getvalue()

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


    async def send_message(self, text: str):
        full_text = await self.finally_text(text)
        await self._route_and_send("message", full_text)

    async def send_media(self, photo: list[tuple[str, bytes]], video: list[tuple[str, bytes]], text: str):
        full_text = await self.finally_text(text)
        await self._route_and_send("media", photo, video, full_text)

    async def send_audio(self, audio: bytes):
        await self._route_and_send("audio", audio)

    async def send_document(self, docs: list[tuple[str, bytes]], text: str):
        full_text = await self.finally_text(text)
        await self._route_and_send("document", docs, full_text)


    async def _route_and_send(self, action:str, *args, **kwargs):
        if "dms=" in self.who_secret:
            platform = "vk"
        elif "dGc=" in self.who_secret:
            platform = "tg"
        else:
            await self.err_end_chat(texts["err_secret"])
            return

        user_id = await db.getUserID(platform, self.who_secret)
        if not user_id:
            await self.err_end_chat(texts["user_not_found"])
            return

        method_name = f"send_{action}_{platform}"
        target_func = getattr(self, method_name, None)

        if target_func == None:
            print(f"Метод {method_name} не реализован")
            return
        await target_func(user_id, *args, **kwargs)


    async def send_message_vk(self, user_id: int, text: str):
        await self.send_vk(user_id, text)

    async def send_message_tg(self, user_id: int, text: str):
        await tg_bot.send_message(user_id, text, parse_mode="HTML")

    async def send_document_tg(self, user_id: int, docs:list[tuple[str, list]], text:str):
        media = await self.media_update_tg(InputMediaDocument, docs)
        await self.add_caption_tg(InputMediaDocument, media, media[-1], text)
        await tg_bot.send_media_group(user_id, media)

    async def send_document_vk(self, user_id, docs: list[tuple[str, bytes]], text: str):
        at_doc = await self.media_update_vk(doc_uploader, docs, user_id)
        final_attachment = ",".join(at_doc)
        await self.send_vk(user_id, text, final_attachment)

    async def send_audio_tg(self, user_id: int, audio_raw: bytes):
        audio = BufferedInputFile(file=audio_raw, filename="audio.ogg")
        await tg_bot.send_message(chat_id=user_id, text=self.head, parse_mode="HTML")
        await tg_bot.send_voice(chat_id=user_id, voice=audio)

    async def send_audio_vk(self, user_id: int, audio: bytes):
        audio_buffer = io.BytesIO(audio)
        audio_buffer.name = "voice.ogg"

        attachment = await doc_uploader.upload(
            file_source=audio_buffer, 
            peer_id=user_id,
            type="audio_message" 
        )
        await self.send_vk(user_id, self.head, str(attachment))

    #TODO Понять почему отправляется через раз
    async def send_media_vk(self, user_id: int, photo: list[tuple[str, bytes]], video: list[tuple[str, bytes]], text: str):
        photo_at = await self.media_update_vk(photo_uploader, photo, user_id)
        if photo and video:
            await asyncio.sleep(0.8)
        video_at = await self.media_update_vk(doc_uploader, video, user_id)
        final_attachment = ",".join(photo_at + video_at)
        await self.send_vk(user_id, text, final_attachment)

    async def send_media_tg(self, user_id: int, photo: list[tuple[str, bytes]], video: list[tuple[str, bytes]], text: str):
        photo_media = await self.media_update_tg(InputMediaPhoto, photo)
        video_media = await self.media_update_tg(InputMediaVideo, video)
        media = photo_media + video_media
        if not media:
            return

        if text:
            if isinstance(media[0], InputMediaPhoto):
                await self.add_caption_tg(InputMediaPhoto, media, media[0], text)
            else:
                await self.add_caption_tg(InputMediaVideo, media, media[0], text)

        await tg_bot.send_media_group(user_id, media)


    async def media_update_vk(self, uploader: DocMessagesUploader | PhotoMessageUploader, media: list[tuple[str, bytes]], user_id: int):
        at = []
        if media:
            for title, m_bytes in media:
                data = io.BytesIO(m_bytes)
                min_at = await uploader.upload(
                    file_source=data,
                    peer_id=user_id,
                    title=title
                )
                at.append(min_at)
                await asyncio.sleep(0.3)
        return at

    async def media_update_tg(self, 
                              Input: InputMediaVideo | InputMediaDocument | InputMediaPhoto, 
                              media: list[tuple[str, bytes]]):
        m = []
        if media:
            for title, m_bytes in media:
                m.append(
                    Input(
                        media=BufferedInputFile(
                            file=m_bytes,
                            filename=title
                        )
                    )
                )

        return m

    async def add_caption_tg(self, 
                             type_media: InputMediaVideo | InputMediaDocument | InputMediaPhoto, 
                             media: list[tuple[str, bytes]], 
                             position: tuple[str, bytes], 
                             text: str):

        index = media.index(position)
        media[index] = type_media(
            media=position.media,
            caption=text, 
            parse_mode="HTML"
        )

    async def send_vk(self, peer_id: int, text: str, attachment:str=None):
        try:
            await vk_bot.api.messages.send(
                peer_id=peer_id,
                message=text,
                attachment=attachment, 
                random_id=random.randint(0, 2**31 - 1)
            )
        except Exception as e:
            print(f"Ошибка отправки в ВК: {e}")


    async def info_for_user(self, text: str, keyboard=None):
        if "dms=" in self.secret:
            params = {
                "peer_id": self.user_id,
                "message": text,
                "random_id": random.randint(0, 2**31 - 1)
            }
            if keyboard:
                params["keyboard"] = keyboard.get_json()
            await vk_bot.api.messages.send(**params)

        elif "dGc=" in self.secret:
            await tg_bot.send_message(self.user_id, text, reply_markup=keyboard)


class Users:
    @staticmethod
    async def get_user(mes:str, user_id:int) -> User:
        if mes == "vk":
            return await Users.get_user_vk(user_id)

        elif mes == "tg":
            return await Users.get_user_tg(user_id)
        
    @staticmethod
    async def get_user_vk(user_id: int) -> User:
        if user_id not in vk_usrs:
            usr = User(user_id, mes="vk")
            vk_usrs[user_id] = usr
            await usr.create("vk")
        return vk_usrs[user_id]

    @staticmethod
    async def get_user_tg(user_id: int) -> User:
        if user_id not in tg_usrs:
            usr = User(user_id, mes="tg")
            tg_usrs[user_id] = usr
            await usr.create("tg")
        return tg_usrs[user_id]
