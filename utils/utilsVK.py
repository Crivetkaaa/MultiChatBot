from vkbottle.bot import Message, MessageEvent

async def getFullName(message: Message|MessageEvent) -> tuple[str, str]:
    if type(message) == Message:
        usr_info = await message.get_user(fields=["screen_name"])
    else:
        user_info = await message.ctx_api.users.get(
        user_ids=[message.object.user_id], 
        fields=["screen_name"]
        )
        usr_info = user_info[0]
    full_name = usr_info.last_name + " " + usr_info.first_name
    url = f"https://vk.ru/{usr_info.screen_name}"
    return (full_name, url)