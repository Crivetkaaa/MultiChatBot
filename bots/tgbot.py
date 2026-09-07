import asyncio
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from config import tg_bot as bot
from config import dp
from classes.user import Users
from classes.media import MediaType, StickerType
from services.services_config import Manager
from resours import texts
import utils.utils as Utils
from aiogram import Router
from aiogram.types import CallbackQuery
from .basebot import BaseBot


router = Router()


@router.callback_query()
async def callback(c: CallbackQuery):
    usr = await Users.get_user("tg", c.from_user.id)
    await BaseBot.callback_handler(usr, c.data, c, "tg")            
    await c.answer()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    await BaseBot.start_handler(usr) 


@dp.message(Command("status"))
async def status_handler(message: Message):
    usr = await Users.get_user("tg", message.chat.id)
    await BaseBot.status_handler(usr)

@dp.message(Command("message"))
@Utils.split_text
async def message_handler(message: Message, secret: str = None, chat_name: str = None) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    await BaseBot.message_handler(usr, secret, chat_name, message, "tg")

@dp.message(Command("quit"))
async def quit_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    await BaseBot.quit_handler(usr)


@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    await BaseBot.help_handler(usr)

@dp.message()
async def default_handler(message: Message, album: list[Message] = None) -> None:
    if message.media_group_id and album is None:
        return

    usr = await Users.get_user("tg", message.chat.id)

    if not usr.in_message: 
        await Manager.info_for_user(usr, texts["not_in_chat"])
        return

    try:
        if message.voice:
            audio = await Manager.tg.download_file_tg(message.voice.file_id)
            await Manager.send_audio(usr, audio)
            return

        if message.sticker:
            sticker = await Manager.tg.download_file_tg(message.sticker.file_id)
            if message.sticker.is_animated:
                await Manager.info_for_user(usr, texts['err_sticker'])
                return
            elif message.sticker.is_video:
                stic = await Utils.createSticker(StickerType.VIDEO, "s.webm", sticker)                                    
            else:
                stic = await Utils.createSticker(StickerType.PHOTO, "s.webp", sticker)
            await Manager.send_sticker(usr, stic)
            return

        messages = album if album else [message]

        media = []
        caption = None

        for msg in messages:
            if msg.caption:
                caption = msg.caption

            if msg.photo:
                photo_bytes = await Manager.tg.download_file_tg(msg.photo[-1].file_id)
                photo = await Utils.createMedia(MediaType.PHOTO, "p.jpg", photo_bytes)
                media.append(photo)

            elif msg.video:
                video_bytes = await Manager.tg.download_file_tg(msg.video.file_id)
                video = await Utils.createMedia(MediaType.VIDEO, "v.mp4", video_bytes)
                media.append(video)

            elif msg.document:
                doc_bytes = await Manager.tg.download_file_tg(msg.document.file_id)
                doc = await Utils.createMedia(MediaType.DOCUMENT, msg.document.file_name, doc_bytes)
                media.append(doc)

        if media:
            await Manager.send_media(usr, media, caption)
            return
        
        if message.text is not None:
            await Manager.send_message(usr, message.text)
            return

        await Manager.info_for_user(usr, texts["err_type"])
        
    except Exception as e:
        await Manager.info_for_user(usr, texts["err"])
        print(e)


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
