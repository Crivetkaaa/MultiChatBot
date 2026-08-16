import asyncio 
from classes.user import Users
from vkbottle.bot import Message
from config import vk_bot as bot
from resours import texts


processed_messages = set()


async def check_secret(secret):
    if len(secret) != 64:
        return False
    return True 


@bot.on.private_message(text=["/start", "начать"])
async def start_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    await usr.info_for_user(usr.secret)
    

@bot.on.private_message(text=["/message <secret>", "переписка <secret>"])
async def message(message: Message, secret: str = None):
    usr = await Users.get_user("vk", message.peer_id) 
    if not usr.in_message:
        if secret != None:
            res = await check_secret(secret.split(":")[1])
            if not res:
                await usr.info_for_user("Ноу")
                return 
            
        usr_info = await message.get_user(fields=["screen_name"])
        full_name = usr_info.last_name + " " + usr_info.first_name
        url = f"https://vk.ru/{usr_info.screen_name}"
        await usr.start_chat(secret, full_name, url, "vk")
        await usr.info_for_user("Вы начали чат")
    else:
        await usr.info_for_user("Вы уже в диалоге. Завершите его командой /quit")

@bot.on.private_message(text="/quit")
async def default_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)

    if usr.in_message:
        await usr.end_chat()
        await usr.info_for_user("Чат закончен")
    else: 
        await usr.info_for_user("Вы не состоите в чате")


@bot.on.private_message(text=["/help", "помощь"])
async def vk_help_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    await usr.info_for_user(texts["help"])


@bot.on.private_message()
async def default_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    if not usr.in_message:
        await usr.info_for_user("Вы не в диалоге")
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
                    audio = await usr.download_audio_vk(attach.audio_message)
                    await usr.send_audio(audio)
                    return

                if attach.video:
                    await usr.info_for_user("Вк ограничивает работу с видео.")
                    return

            photos_to_send = []
            for attach in full_attachments:
                if attach.photo:
                    photo_bytes = await usr.download_photo_vk(attach.photo)
                    photos_to_send.append(photo_bytes)

            if photos_to_send:
                await usr.send_media(photo=photos_to_send, video=None, text=message.text)
                return

        if message.text:
            await usr.send_message(message.text)
            return

        await usr.info_for_user("Данный вид сообщений не поддерживается")

    except Exception as e:
        await usr.info_for_user("Упс... Что-то пошло не так")
        print(f"Ошибка в обработчике ВК: {e}")


async def clear_msg_cache(msg_id: int):
    await asyncio.sleep(2.0)
    processed_messages.discard(msg_id)


async def main():
    print("VKBottle запущен...")
    await bot.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
