import secrets
import base64
from config import tg_usrs, vk_usrs
from database import db


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
