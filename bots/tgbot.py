import asyncio
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from config import tg_bot as bot
from config import dp
from classes.user import Users
from classes.media import MediaType, StickerType
from services.service_manager import Manager
from services.tg import tgService
from resours import texts
from classes.utils import Utils
from utils.utilsTG import Utils as TGUtils
from aiogram import Router
from aiogram.types import CallbackQuery
from keyboards.keyboardsTG import KeybordsTG 


router = Router()


@router.callback_query()
async def callback(c: CallbackQuery):
    usr = await Users.get_user("tg", c.from_user.id)

    command, who_secret = c.data.split("|")
    match command:
        case "start_chat":
            res = await Utils.check_secret(who_secret)
            if not res:
                await Manager.info_for_user(usr, texts["err_secret"])
                return

            full_name, url = await TGUtils.getFullName(c)
        
            await usr.start_chat(who_secret, full_name, url, "tg")
            await Manager.info_for_user(usr, texts["start_chat"])

        case _:
            await Manager.info_for_user(usr, "err")
            
    await c.answer()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    text = texts["help"] + "\n\n" + f'{texts["start_bottom"]} \n{usr.secret}'
    await Manager.info_for_user(usr, text)


@dp.message(Command("status"))
async def status_handler(message: Message):
    usr = await Users.get_user("tg", message.chat.id)
    if usr.in_message:
        await Manager.info_for_user(usr, f'{texts["status"]} \n{usr.who_secret}')
    else:
        await Manager.info_for_user(usr, texts["not_in_chat"])


@dp.message(Command("message"))
@TGUtils.split_text
async def message_handler(message: Message, secret: str = None, chat_name: str = None) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    if usr.in_message:
        await Manager.info_for_user(usr, texts["err_new_chat"])
        return

    if secret:
        res = await Utils.check_secret(secret)
        if not res:
            await Manager.info_for_user(usr, texts["err_secret"])
            return

    full_name, url = await TGUtils.getFullName(message)
        
    await usr.start_chat(secret, full_name, url, "tg")
    await Manager.info_for_user(usr, texts["start_chat"])

    if chat_name:
        await usr.addChat(chat_name)


@dp.message(Command("quit"))
async def quit_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)

    chats = await usr.userChats()
    keyboard = await KeybordsTG.userChats(chats)

    if usr.in_message:
        await usr.end_chat()
        await Manager.info_for_user(usr, texts["end_chat"], keyboard)
    else:
        await Manager.info_for_user(usr, texts["not_in_chat"], keyboard)


@dp.message(Command("help"))
async def tg_help_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    await Manager.info_for_user(usr, texts["help"])


@dp.message()
async def echo_handler(message: Message, album: list[Message] = None) -> None:
    if message.media_group_id and album is None:
        return

    usr = await Users.get_user("tg", message.chat.id)

    if not usr.in_message: 
        await Manager.info_for_user(usr, texts["not_in_chat"])
        return

    try:
        if message.voice:
            audio = await tgService.download_file_tg(message.voice.file_id)
            await Manager.send_audio(usr, audio)
            return

        if message.sticker:
            sticker = await tgService.download_file_tg(message.sticker.file_id)
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
                photo_bytes = await tgService.download_file_tg(msg.photo[-1].file_id)
                photo = await Utils.createMedia(MediaType.PHOTO, "p.jpg", photo_bytes)
                media.append(photo)

            elif msg.video:
                video_bytes = await tgService.download_file_tg(msg.video.file_id)
                video = await Utils.createMedia(MediaType.VIDEO, "v.mp4", video_bytes)
                media.append(video)

            elif msg.document:
                doc_bytes = await tgService.download_file_tg(msg.document.file_id)
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
