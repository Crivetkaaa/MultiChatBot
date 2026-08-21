from __future__ import annotations
from resours import texts
from database.database import db
import random
from services.vk import vkService, VkService
from services.tg import tgService, TgService

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from classes.user import User

class ServiceManager:
    def __init__(self, vk:VkService, tg:TgService):
        self.vk = vk
        self.tg = tg

    async def _route_and_send(self, action:str, usr: User, *args, **kwargs):
            if "dms=" in usr.who_secret:
                platform = self.vk
                p = "vk"
            elif "dGc=" in usr.who_secret:
                platform = self.tg
                p = "tg"
            else:
                await usr.err_end_chat(texts["err_secret"])
                return
    
            user_id = await db.getUserID(p, usr.who_secret)
            if not user_id:
                await usr.err_end_chat(texts["user_not_found"])
                return
    
            method_name = f"send_{action}"
            target_func = getattr(platform, method_name, None)
    
            if target_func == None:
                print(f"Метод {method_name} не реализован")
                return
            await target_func(user_id, *args, **kwargs)

    async def send_message(self, usr:User, text: str):
        finally_text = await usr.finally_text(text)
        await self._route_and_send("message", usr, finally_text)

    async def send_audio(self, usr:User, audio: bytes):
        full_text = await usr.finally_text("")
        await self._route_and_send("audio", usr, audio, full_text)

    async def send_media(self, usr:User, media: list[tuple[str, bytes]], text: str):
        full_text = await usr.finally_text(text)
        await self._route_and_send("media", usr, media, full_text)

    async def info_for_user(self, usr:User, keyboard, text: str):
        if "dms=" in usr.secret:
            params = {
                "peer_id": usr.user_id,
                "message": text,
                "random_id": random.randint(0, 2**31 - 1)
            }
            if keyboard:
                params["keyboard"] = keyboard.get_json()
            await self.vk.info_for_user(**params)

        elif "dGc=" in usr.secret:
            await self.tg.info_for_user(usr.user_id, text, keyboard)

        
Manager = ServiceManager(vkService, tgService)
