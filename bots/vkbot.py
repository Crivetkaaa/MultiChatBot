import asyncio 
from classes.user import Users
from vkbottle.bot import Message
from config import vk_bot as bot
from resours import texts


async def check_secret(secret):
    if len(secret) != 64:
        return False
    return True 


@bot.on.private_message(text=["/start", "начать"])
async def start_handler(message: Message):
    user_info = await message.get_user(fields=["screen_name"])
    print(user_info.screen_name)
    usr = await Users.get_user("vk", message.peer_id)
    await usr.info_for_user(usr.secret)
    

@bot.on.private_message(text=["/message <secret>", "переписка <secret>"])
async def message(message: Message, secret: str = None):
    usr = await Users.get_user("vk", message.peer_id) 
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


@bot.on.private_message(text="/quit")
async def default_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    await usr.end_chat()
    await usr.info_for_user("Чат закончен")


@bot.on.private_message(text=["/help", "помощь"])
async def vk_help_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    # Отправляем подготовленный текст справки
    await usr.info_for_user(texts["help"])


@bot.on.private_message()
async def default_handler(message: Message):
    usr = await Users.get_user("vk", message.peer_id)
    if usr.in_message:
        try:
            await usr.send_message(message.text)
        except:
            await usr.info_for_user("Данный вид сообщений не поддерживается")

    else:
        await usr.info_for_user("Вы не в диалоге")



async def main():
    print("VKBottle запущен...")
    await bot.run_polling()


if __name__ == "__main__":
    asyncio.run(main())

