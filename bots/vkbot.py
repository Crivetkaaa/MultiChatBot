import asyncio 
from classes.user import Users
from vkbottle.bot import Message
from services.service_manager import Manager
from config import vk_bot as bot
from services.vk import vkService
from resours import texts
from classes.media import MediaType, StickerType
from classes.utils import Utils


processed_messages = set()


async def check_secret(secret):
    if len(secret) != 64:
        return False
    return True 


@bot.on.private_message(text=["/start", "начать"])
async def start_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    text = texts["help"] + "\n\n" + f'{texts["start_bottom"]} {usr.secret}'
    await Manager.info_for_user(usr, text)
    

@bot.on.private_message(text="/status")
async def status_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    if usr.in_message:
        await Manager.info_for_user(usr, f'{texts["status"]} {usr.who_secret}')
    else:
        await Manager.info_for_user(usr, None, texts["not_in_chat"])


@bot.on.private_message(text="/message <secret>")
async def message(message: Message, secret: str = None):
    usr = await Users.get_user("vk", message.peer_id) 
    if not usr.in_message:
        if secret != None:
            res = await Utils.check_secret(secret)
            if not res:
                await Manager.info_for_user(usr, None, texts["err_secret"])
                return 
            
        usr_info = await message.get_user(fields=["screen_name"])
        full_name = usr_info.last_name + " " + usr_info.first_name
        url = f"https://vk.ru/{usr_info.screen_name}"
        await usr.start_chat(secret, full_name, url, "vk")
        await Manager.info_for_user(usr, None, texts["start_chat"])
    else:
        await Manager.info_for_user(usr, None, texts["err_new_chat"])


@bot.on.private_message(text="/quit")
async def default_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)

    if usr.in_message:
        await usr.end_chat()
        await Manager.info_for_user(usr, None, texts["end_chat"])
    else: 
        await Manager.info_for_user(usr, None, texts["not_in_chat"])


@bot.on.private_message(text="/help")
async def vk_help_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    await Manager.info_for_user(usr, None, texts["help"])


@bot.on.private_message()
async def default_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    if not usr.in_message:
        await Manager.info_for_user(usr, None, texts["not_in_chat"])
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
                    await Manager.info_for_user(usr, None, texts["vk_video_err"])
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

        await Manager.info_for_user(usr, None, texts["err_type"])

    except Exception as e:
        await Manager.info_for_user(usr, None, texts["err"])
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
