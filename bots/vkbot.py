import asyncio 
from classes.user import Users
from vkbottle.bot import Message
from services.service_manager import Manager
from config import vk_bot as bot
from services.vk import vkService
from resours import texts
from classes.media import MediaType, StickerType
from classes.utils import Utils
from keyboards.keyboardsVK import KeyboardsVK
from vkbottle.bot import MessageEvent
from vkbottle_types.events import GroupEventType


processed_messages = set()


@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def callback_handler(event: MessageEvent):
    usr = await Users.get_user("vk", event.object.user_id)
    payload = event.payload or {}
    raw_command = payload.get("cmd")

    if not raw_command:
        await Manager.send_message(usr, "Что-то пощло не так")
        return

    command, who_secret = raw_command.split("|")

    match command:
        case "start_chat":
            full_name, url = await Utils.getFullNameVk(event)
            await usr.start_chat(who_secret, full_name, url, "vk")
            await Manager.info_for_user(usr, texts["start_chat"])
        case _:
            await Manager.info_for_user(usr, "бля")

    await event.send_empty_answer()


@bot.on.private_message(text=["/start", "начать"])
async def start_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    text = texts["help"] + "\n\n" + f'{texts["start_bottom"]} \n{usr.secret}'
    await Manager.info_for_user(usr, text)
    

@bot.on.private_message(text="/status")
async def status_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    if usr.in_message:
        await Manager.info_for_user(usr, f'{texts["status"]} {usr.who_secret}')
    else:
        await Manager.info_for_user(usr, texts["not_in_chat"])


@bot.on.private_message(text="/message <secret> <chat_name>")
async def message(message: Message, secret: str = None, chat_name = None):
    usr = await Users.get_user("vk", message.peer_id) 

    if usr.in_message:
        await Manager.info_for_user(usr, texts["err_new_chat"])
        return

    if secret != None:
        res = await Utils.check_secret(secret)
        if not res:
            await Manager.info_for_user(usr, texts["err_secret"])
            return 


    full_name, url = await Utils.getFullNameVk(message)
    await usr.start_chat(secret, full_name, url, "vk")
    await Manager.info_for_user(usr, texts["start_chat"])

    if chat_name:
        await usr.addChat(chat_name)


@bot.on.private_message(text="/quit")
async def default_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)

    chats = await usr.userChats()
    keyboard = await KeyboardsVK.userChats(chats)

    if usr.in_message:
        await usr.end_chat()
        await Manager.info_for_user(usr, texts["end_chat"], keyboard)
    else: 
        await Manager.info_for_user(usr, texts["not_in_chat"], keyboard)


@bot.on.private_message(text="/help")
async def vk_help_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    await Manager.info_for_user(usr, texts["help"])


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
                    audio = await vkService.download_audio_vk(attach.audio_message)
                    await Manager.send_audio(usr, audio)
                    return

                if attach.sticker:
                    sticker = await vkService.download_sticker_vk(attach.sticker.sticker_id)
                    stic = await Utils.createSticker(StickerType.PHOTO, "s.png", sticker)
                    await Manager.send_sticker(usr, stic)
                    return

                if attach.video:
                    await Manager.info_for_user(usr, texts["vk_video_err"])
                    return

            media = []
            for attach in full_attachments:
                if attach.photo:
                    photo_bytes = await vkService.download_photo_vk(attach.photo)
                    photo = await Utils.createMedia(MediaType.PHOTO, "photo.jpg", photo_bytes)
                    media.append(photo)

                elif attach.doc:
                    doc_bytes = await vkService.download_doc_vk(attach.doc)
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
