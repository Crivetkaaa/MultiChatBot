import asyncio
from bots.tgbot import main as tg_main
from bots.vkbot import main as vk_main
import logging
import sys
import os
from database import db
from classes.user import User
from config import vk_usrs, tg_usrs


async def main():
    await db.connect()

    vk_res, tg_res = await db.getUsers()
    for vr in vk_res:
        vk_id, secret = vr[0], vr[1]
        vk_usrs[vk_id] = User(vk_id, secret)

    for tr in tg_res:
        tg_id, secret = tr[0], tr[1]
        tg_usrs[tg_id] = User(tg_id, secret)
    
    try:
        await asyncio.gather(
            tg_main(),
            vk_main()
        )
    except Exception as e:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот-система остановлена пользователем.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)