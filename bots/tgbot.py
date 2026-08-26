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


async def check_secret(secret: str) -> bool:
    if len(secret) != 64:
        return False
    return True


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    text = texts["help"] + "\n\n" + f'{texts["start_bottom"]} {usr.secret}'
    await Manager.info_for_user(usr, text)


@dp.message(Command("status"))
async def status_handler(message: Message):
    usr = await Users.get_user("tg", message.chat.id)
    if usr.in_message:
        await Manager.info_for_user(usr, f'{texts["status"]} {usr.who_secret}')
    else:
        await Manager.info_for_user(usr, None, texts["not_in_chat"])


@dp.message(Command("message"))
async def message_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    if usr.in_message:
        await Manager.info_for_user(usr, None, texts["err_new_chat"])
        return


    _, secret_args = message.text.split(maxsplit=1)
    print(secret_args)
    if secret_args:
        res = await Utils.check_secret(secret_args)
        if not res:
            await Manager.info_for_user(usr, None, texts["err_secret"])
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
    await Manager.info_for_user(usr, None, texts["start_chat"])


@dp.message(Command("quit"))
async def quit_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    if usr.in_message:
        await usr.end_chat()
        await Manager.info_for_user(usr, None, texts["end_chat"])
    else:
        await Manager.info_for_user(usr, None, texts["not_in_chat"])


@dp.message(Command("help"))
async def tg_help_handler(message: Message) -> None:
    usr = await Users.get_user("tg", message.chat.id)
    await Manager.info_for_user(usr, None, texts["help"])


@dp.message()
async def echo_handler(message: Message, album: list[Message] = None) -> None:
    if message.media_group_id and album is None:
        return

    usr = await Users.get_user("tg", message.chat.id)
    
    if usr.in_message:
        try:
            if message.voice:
                audio = await tgService.download_file_tg(message.voice.file_id)
                await Manager.send_audio(usr, audio)
                return

            if message.sticker:
                sticker = await tgService.download_file_tg(message.sticker.file_id)
                if message.sticker.is_animated:
                    pass
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

            await Manager.info_for_user(usr, None, texts["err_type"])
            
        except Exception as e:
            await Manager.info_for_user(usr, None, texts["err"])
            print(e)
    else:
        await Manager.info_for_user(usr, None, texts["not_in_chat"])


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
