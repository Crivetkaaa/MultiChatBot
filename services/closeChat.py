from config import vk_usrs, tg_usrs
import time
import asyncio
from resours import texts
from classes.user import User

async def closeChat_for(users_dict:dict[int, User]):
    for usr in users_dict.values():
        if usr.last_message != None:
            if time.time() - usr.last_message > 30*60:
                await usr.end_chat() 
                await usr.err_end_chat(texts["time_out"])



async def closeChat():
    while True:
        await closeChat_for(vk_usrs)
        await closeChat_for(tg_usrs)
        
        await asyncio.sleep(30*60)