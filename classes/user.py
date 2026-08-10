import secrets
import random
import base64
import aiohttp
from config import tg_usrs, vk_usrs
from database import db
from config import vk_bot, tg_bot
from vk_api.keyboard import VkKeyboard
from aiogram.types import BufferedInputFile


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
            text = f"Сообщение из {from_}\nОт: {name}\nИз: {url}\n\n"
            

        elif "dGc=" in secret:
            text = f"Сообщение из {from_}\nОт: <a href=\"{url}\">{name}</a>\n\n"

        else:
            text = f"Сообщение из {from_}\nОт: {name}\n\n"

        self.head = text

    async def start_chat(self, secret, full_name, url, from_):
        await self.generate_head(secret, full_name, url, from_)
        self.in_message = True
        self.who_secret = secret
        

    async def end_chat(self):
        self.in_message = False
        self.who_secret = None
        self.head = None

    async def create(self, mes:str):
        await db.createUser(mes, self.user_id, self.secret)

    async def download_audio_tg(self, file_id):
        file = await tg_bot.get_file(file_id)
        file_path = file.file_path
        file_in_memory = await tg_bot.download_file(file_path)
        file_in_memory.seek(0)
        audio_bytes = file_in_memory.read()
        return audio_bytes

    async def download_audio_vk(self, audio):
        ogg_url = audio.link_ogg
        async with aiohttp.ClientSession() as session:
            async with session.get(ogg_url) as response:
                audio_bytes = await response.read()

        voice_file = BufferedInputFile(audio_bytes, filename="voice.ogg")
        return voice_file

    async def worker(self, mes, function, message):
        user_id = await db.getUserID(mes, self.who_secret)
        if not user_id:
            await self.info_for_user("Пользователь не найден чат закрыт")
            await self.end_chat()
            return
        await function(user_id, message)

    async def send_audio(self, audio):
        if "dms=" in self.who_secret:
            mes="vk"
            await self.worker(mes, self.send_audio_vk, audio)

        elif "dGc=" in self.who_secret:
            mes="tg"
            await self.worker(mes, self.send_audio_tg, audio)
        else:            
            await self.info_for_user("Ошибка в ключе пользователя чат закрыт")
            await self.end_chat()

    async def send_audio_tg(self, user_id, audio):
        await tg_bot.send_message(
            chat_id=user_id,
            text=self.head,
            parse_mode="HTML"
        )

        await tg_bot.send_voice(
            chat_id=user_id,
            voice=audio
        )

    async def send_audio_vk(self, user_id, audio):
        upload_server = await vk_bot.api.docs.get_messages_upload_server(
            type="audio_message", 
            peer_id=user_id
        )
        upload_url = upload_server.upload_url

        form_data = aiohttp.FormData()
        form_data.add_field('file', audio, filename='voice.ogg', content_type='audio/ogg')

        async with aiohttp.ClientSession() as session:
            async with session.post(upload_url, data=form_data) as response:
                upload_result = await response.json()
                
        if "file" not in upload_result:
            return

        saved_doc = await vk_bot.api.docs.save(
            file=upload_result["file"],
            title="voice.ogg"
        )
        
        if isinstance(saved_doc, list):
            doc_obj = saved_doc[0].audio_message if hasattr(saved_doc[0], 'audio_message') else saved_doc[0].doc
        else:
            doc_obj = getattr(saved_doc, "audio_message", getattr(saved_doc, "doc", None))
            if not doc_obj and hasattr(saved_doc, 'response'):
                doc_obj = saved_doc.response.audio_message

        attachment = f"doc{doc_obj.owner_id}_{doc_obj.id}"

        await vk_bot.api.messages.send(
            peer_id=user_id,
            message=self.head,
            attachment=attachment,
            random_id=random.randint(0, 2**31 - 1)
        )

    async def send_message(self, text:str):
        msg = self.head + text
        if "dms=" in self.who_secret:
            mes="vk"
            await self.worker(mes, self.send_to_vk, msg)

        elif "dGc=" in self.who_secret:
            mes="tg"
            await self.worker(mes, self.send_to_tg, msg)
            
        else:            
            await self.info_for_user("Ошибка в ключе пользователя чат закрыт")
            await self.end_chat()

    async def send_to_vk(self, who_id: int, text: str):
        params = {
            "peer_id": who_id,
            "message": text,
            "random_id": random.randint(0, 2**31 - 1)
        }

        await vk_bot.api.messages.send(**params)

    async def send_to_tg(self, who_id, text):
        await tg_bot.send_message(who_id, text, parse_mode="HTML")

    async def info_for_user(self, text: str, keyboard=None):

        if "dms=" in self.secret:
            await self.info_for_user_vk(text, keyboard)

        elif "dGc=" in self.secret:
            await self.info_for_user_tg(text, keyboard)

    async def info_for_user_vk(self, text: str, keyboard: VkKeyboard=None):
        params = {
            "peer_id": self.user_id,
            "message": text,
            "random_id": random.randint(0, 2**31 - 1)
        }
        if keyboard:
            params["keyboard"] = keyboard.get_json()
            
        await vk_bot.api.messages.send(**params)

    async def info_for_user_tg(self, text, keyboard):
        await tg_bot.send_message(self.user_id, text, keyboard)

        
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

