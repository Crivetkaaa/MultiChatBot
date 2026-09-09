import asyncio
from bots.tgbot import main as tg_main
from bots.tgbot import router
from bots.vkbot import main as vk_main
from bots.maxbot import main as mx_main
import logging
import sys
import os
from database import db
from classes.user import User
from config import usrs, mes, dp
from services.closeChat import closeChat


async def usersList(list_usrs, users, m):
    for user_id, secret in users:
        list_usrs[user_id] = User(user_id, secret, m)

async def main():
    dp.include_router(router)
    await db.connect()

    for list_usrs, m in zip(usrs, mes):
        res = await db.getUsers(m)

        await usersList(list_usrs, res, m)

    try:
        await asyncio.gather(
            tg_main(),
            # vk_main(),
            # mx_main(),

            closeChat()
        )
    except Exception as e:
        print(e)
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