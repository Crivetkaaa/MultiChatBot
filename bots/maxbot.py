from config import mx_bot as bot, mx_dp as dp
from maxapi.types.updates.bot_started import BotStarted
from maxapi.types.updates.message_created import MessageCreated
from maxapi.types import Command
from classes.user import Users
from bots.basebot import BaseBot
from maxapi.types.updates.message_callback import MessageCallback
from services.services_config import Manager
from resours import texts
from classes.media import MediaType, StickerType
import utils.utils as Utils


@dp.message_callback()
async def callback_handler(event: MessageCallback):
    usr = await Users.get_user("mx",  event.get_ids()[1])
    payload = event.callback.payload if event.callback else None
    await BaseBot.callback_handler(usr, payload, event, "mx")
    await event.answer()

@dp.bot_started()
async def start_handler(event: BotStarted):
    usr = await Users.get_user("mx", event.get_ids()[1]) 
    await BaseBot.start_handler(usr)


@dp.message_created(Command("start"))
async def start_handler_2(event: MessageCreated):
    usr = await Users.get_user("mx", event.get_ids()[1])
    await BaseBot.start_handler(usr)


@dp.message_created(Command("status"))
async def status_handler(event: MessageCreated):
    usr = await Users.get_user("mx", event.get_ids()[1])
    await BaseBot.status_handler(usr)


@dp.message_created(Command("quit"))
async def quit_handler(event: MessageCreated):
    usr = await Users.get_user("mx", event.get_ids()[1])
    await BaseBot.quit_handler(usr)


@dp.message_created(Command("message"))
@Utils.split_text
async def message_handler(event: MessageCreated, secret: str=None, chat_name:str = None):
    usr = await Users.get_user("mx", event.get_ids()[1])
    await BaseBot.message_handler(usr, secret, chat_name, event, "max")


@dp.message_created(Command("help"))
async def help_handler(event: MessageCreated):
    usr = await Users.get_user("mx", event.get_ids()[1])
    await BaseBot.quit_handler(usr)


@dp.message_created()
async def default_hendler(event: MessageCreated):
    usr = await Users.get_user("mx", event.get_ids()[1])

    if not usr.in_message:
        await Manager.info_for_user(usr, texts["not_in_chat"])
        return
    attachments = event.message.body.attachments

    media = []
    try:
        for attach in attachments:
            if attach.type == "sticker":
                sticker_bytes = await Manager.mx.download_file(attach.payload.url)
                sticker = await Utils.createSticker(StickerType.PHOTO, "p.jpg", sticker_bytes)
                await Manager.send_sticker(usr, sticker)
                return
                

            if attach.type == "image":
                photo_bytes = await Manager.mx.download_file(attach.payload.url)
                photo = await Utils.createMedia(MediaType.PHOTO, "p.jpg", photo_bytes)
                media.append(photo)

            if attach.type == "video":
                video_bytes = await Manager.mx.download_file(attach.payload.url)
                video = await Utils.createMedia(MediaType.VIDEO, "v.mp4", video_bytes)
                media.append(video)

            if attach.type == "file":
                file_bytes = await Manager.mx.download_file(attach.payload.url)
                file = await Utils.createMedia(MediaType.DOCUMENT, attach.filename, file_bytes)
                media.append(file)

                
        if media:
            await Manager.send_media(usr, media, event.message.body.text)
            return
        if event.message.body.text:
            await Manager.send_message(usr, event.message.body.text)
            return
        await Manager.info_for_user(usr, texts["err_type"])
    except Exception as e:
        print(e)
        await Manager.info_for_user(usr, texts["err"])


async def main():
    print("MaxBot запущен...")
    await dp.start_polling(bot)
