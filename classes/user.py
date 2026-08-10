import secrets
import random
import base64
import aiohttp
import io
from config import tg_usrs, vk_usrs
from database import db
from config import vk_bot, tg_bot
from aiogram.types import BufferedInputFile
from vkbottle import PhotoMessageUploader
from vkbottle import DocMessagesUploader


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

    async def generate_head(self, secret, name, url, from_):
        if "dms=" in secret:
            self.head = f"Сообщение из {from_}\nОт: {name}\nИз: {url}\n\n"
        elif "dGc=" in secret:
            self.head = f"Сообщение из {from_}\nОт: <a href=\"{url}\">{name}</a>\n\n"
        else:
            self.head = f"Сообщение из {from_}\nОт: {name}\n\n"

    async def start_chat(self, secret, full_name, url, from_):
        await self.generate_head(secret, full_name, url, from_)
        self.in_message = True
        self.who_secret = secret

    async def end_chat(self):
        self.in_message = False
        self.who_secret = None
        self.head = None

    async def create(self, mes: str):
        await db.createUser(mes, self.user_id, self.secret)

    async def download_file_tg(self, file_id):
        file = await tg_bot.get_file(file_id)
        file_in_memory = await tg_bot.download_file(file.file_path)
        return file_in_memory.getvalue() 

    async def download_audio_vk(self, audio):
        async with aiohttp.ClientSession() as session:
            async with session.get(audio.link_ogg) as response:
                return await response.read()

    async def download_photo_vk(self, photo):
        best_size = max(photo.sizes, key=lambda size: size.width)
        async with aiohttp.ClientSession() as session:
            async with session.get(best_size.url) as response:
                return await response.read()

    async def _route_and_send(self, action, *args, **kwargs):
        if "dms=" in self.who_secret:
            platform = "vk"
        elif "dGc=" in self.who_secret:
            platform = "tg"
        else:
            await self.info_for_user("Ошибка в ключе пользователя, чат закрыт")
            await self.end_chat()
            return

        user_id = await db.getUserID(platform, self.who_secret)
        if not user_id:
            await self.info_for_user("Пользователь не найден, чат закрыт")
            await self.end_chat()
            return

        method_name = f"send_{action}_{platform}"
        target_func = getattr(self, method_name, None)

        if target_func == None:
            print(f"Метод {method_name} не реализован")
            return
        
        await target_func(user_id, *args, **kwargs)


    async def send_message(self, text: str):
        safe_text = text or ""
        full_text = self.head + safe_text
        await self._route_and_send("message", full_text)

    async def send_photo(self, photo: bytes, text: str):
        safe_text = text or ""
        full_text = self.head + safe_text
        await self._route_and_send("photo", photo, full_text)

    async def send_audio(self, audio: bytes):
        await self._route_and_send("audio", audio)


    async def send_message_vk(self, user_id: int, text: str):
        await vk_bot.api.messages.send(
            peer_id=user_id,
            message=text,
            random_id=random.randint(0, 2**31 - 1)
        )

    async def send_message_tg(self, user_id: int, text: str):
        await tg_bot.send_message(user_id, text, parse_mode="HTML")

    async def send_photo_vk(self, user_id: int, photo: bytes, text: str):
        vk_buffer = io.BytesIO(photo)
        vk_buffer.name = "photo.jpg"

        photo_uploader = PhotoMessageUploader(vk_bot.api)
        vk_attachment = await photo_uploader.upload(vk_buffer)

        await vk_bot.api.messages.send(
            peer_id=user_id,
            message=text,
            attachment=str(vk_attachment),
            random_id=random.randint(0, 2**31 - 1)
        )

    async def send_photo_tg(self, user_id: int, photo: bytes, text: str):
        photo_file = BufferedInputFile(file=photo, filename="photo.jpg")
        await tg_bot.send_photo(user_id, photo_file, caption=text, parse_mode="HTML")

    async def send_audio_tg(self, user_id: int, audio_raw: bytes):
        audio = BufferedInputFile(file=audio_raw, filename="audio.ogg")
        await tg_bot.send_message(chat_id=user_id, text=self.head, parse_mode="HTML")
        await tg_bot.send_voice(chat_id=user_id, voice=audio)

    async def send_audio_vk(self, user_id: int, audio: bytes):
        audio_buffer = io.BytesIO(audio)
        audio_buffer.name = "voice.ogg"

        uploader = DocMessagesUploader(vk_bot.api)
        attachment = await uploader.upload(
            file_source=audio_buffer, 
            peer_id=user_id,
            type="audio_message" 
        )

        await vk_bot.api.messages.send(
            peer_id=user_id,
            message=self.head,
            attachment=str(attachment), 
            random_id=random.randint(0, 2**31 - 1)
        )
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

