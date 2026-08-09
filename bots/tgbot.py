import asyncio
from aiogram import html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from config import tg_bot as bot
from config import dp
from classes.user import Users
from resours import texts


async def check_secret(secret: str) -> bool:
    if len(secret) != 64:
        return False
    return True


@dp.message(CommandStart())
@dp.message(F.text.lower() == "начать")
async def command_start_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    await usr.info_for_user(usr.secret)


@dp.message(Command("message"))
@dp.message(F.text.lower().startswith("переписка "))
async def message_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    
    if message.text.startswith("/message"):
        secret_args = message.text[9:].strip()
    else:
        secret_args = message.text[10:].strip()

    if secret_args:
        parts = secret_args.split(":")
        if len(parts) >= 2:
            res = await check_secret(parts[1])
            if not res:
                await usr.info_for_user("Ноу")
                return
        else:
            await usr.info_for_user("Ноу")
            return

    usr_info = message.from_user
    
    last_name = usr_info.last_name or ""
    first_name = usr_info.first_name or ""
    full_name = f"{last_name} {first_name}".strip()
    
    if usr_info.username:
        url = f"https://t.me/{usr_info.username}"
    else:
        url = f"tg://user?id={usr_info.id}"
        
    await usr.start_chat(secret_args, full_name, url, "tg")
    await usr.info_for_user("Вы начали чат")


# 3. Хэндлер на команду /quit или "выход" (аналог /quit)
@dp.message(Command("quit"))
async def quit_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    await usr.end_chat()
    await usr.info_for_user("Чат закончен")


@dp.message(Command("help"))
@dp.message(F.text.lower() == "помощь")
async def tg_help_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    
    await usr.info_for_user(texts["help"])


@dp.message()
async def echo_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    
    if usr.in_message:
        try:
            if message.text is None:
                raise ValueError("Медиа не поддерживается")
                
            await usr.send_message(message.text)
        except Exception:
            await usr.info_for_user("Данный вид сообщений не поддерживается")
    else:
        await usr.info_for_user("Вы не в диалоге")


async def main() -> None:
    print("Telegram Bot запущен...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import logging
    import sys
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nБот-система остановлена пользователем.")
