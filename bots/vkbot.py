import asyncio 
from classes.user import Users
from vkbottle.bot import Message
from services.services_config import Manager
from config import vk_bot as bot
from resours import texts
from classes.media import MediaType, StickerType
from utils.utils import Utils
from utils.utilsVK import Utils as VKUtils
from vkbottle.bot import MessageEvent
from vkbottle_types.events import GroupEventType
from bots.basebot import BaseBot

processed_messages = set()


@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def callback_handler(event: MessageEvent):
    usr = await Users.get_user("vk", event.object.user_id)
    raw_command = event.payload.get("cmd")
    full_name, url = await VKUtils.getFullName(event)
    await BaseBot.callback_handler(usr, raw_command, full_name, url, "vk")
    await event.send_empty_answer()


@bot.on.private_message(text=["/start", "начать"])
async def start_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    await BaseBot.start_handler(usr)
    

@bot.on.private_message(text="/status")
async def status_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    await BaseBot.status_handler(usr)


@bot.on.private_message(text="/message <secret> <chat_name>")
async def message_full_info(message: Message, secret: str = None, chat_name = None):
    await message_support(message, secret, chat_name)

@bot.on.private_message(text="/message <secret>")
async def message_secret(message: Message, secret: str = None):
    await message_support(message, secret)

@bot.on.private_message(text="/message")
async def message(message: Message):
    await message_support(message)

async def message_support(message:Message, secret:str=None, chat_name:str=None):
    usr = await Users.get_user("vk", message.peer_id) 
    full_name, url = await VKUtils.getFullName(message)
    await BaseBot.message_handler(usr, secret, chat_name, full_name, url, "vk")
    

@bot.on.private_message(text="/quit")
async def quit_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    await BaseBot.quit_handler(usr)


@bot.on.private_message(text="/help")
async def help_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    await BaseBot.help_handler(usr)


@bot.on.private_message()
async def default_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    if not usr.in_message:
        await Manager.info_for_user(usr, texts["not_in_chat"])
        return

    msg_id = message.conversation_message_id
    if msg_id in processed_messages:
        return
    processed_messages.add(msg_id)

    asyncio.create_task(clear_msg_cache(msg_id))

    try:
        full_message = await message.get_full_message()
        full_attachments = full_message.attachments or []

        if full_attachments:
            for attach in full_attachments:
                if attach.audio_message:
                    audio = await Manager.vk.download_audio_vk(attach.audio_message)
                    await Manager.send_audio(usr, audio)
                    return

                if attach.sticker:
                    sticker = await Manager.vk.download_sticker_vk(attach.sticker.sticker_id)
                    stic = await Utils.createSticker(StickerType.PHOTO, "s.png", sticker)
                    await Manager.send_sticker(usr, stic)
                    return

                if attach.video:
                    await Manager.info_for_user(usr, texts["vk_video_err"])
                    return

            media = []
            for attach in full_attachments:
                if attach.photo:
                    photo_bytes = await Manager.vk.download_photo_vk(attach.photo)
                    photo = await Utils.createMedia(MediaType.PHOTO, "photo.jpg", photo_bytes)
                    media.append(photo)

                elif attach.doc:
                    doc_bytes = await Manager.vk.download_doc_vk(attach.doc)
                    doc = await Utils.createMedia(MediaType.DOCUMENT, attach.doc.title, doc_bytes)
                    media.append(doc)

            if media:
                await Manager.send_media(usr, media, text=message.text)
                return

        if message.text:
            await Manager.send_message(usr, message.text)
            return

        await Manager.info_for_user(usr, texts["err_type"])

    except Exception as e:
        await Manager.info_for_user(usr, texts["err"])
        print(f"Ошибка в обработчике ВК: {e}")


async def clear_msg_cache(msg_id: int):
    await asyncio.sleep(2.0)
    processed_messages.discard(msg_id)


async def main():
    print("VKBottle запущен...")
    await bot.run_polling()


if __name__ == "__main__":
    import logging
    import sys
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
