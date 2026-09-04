from .keyboardsMAX import KeyboardsMAX
from .keyboardsTG import KeybordsTG
from .keyboardsVK import KeyboardsVK
from .baseKeyboards import BaseKeyboards

class Keyboards:

    keyboards = {
        "vk": KeyboardsVK,
        "tg": KeybordsTG,
        "mx": KeyboardsMAX,
    }

    @classmethod
    async def getKeyboards(cls, platform: str) -> BaseKeyboards:
        return cls.keyboards[platform]

    @classmethod
    async def userChats(cls, chats, platform):
        if chats:
            kClass = await cls.getKeyboards(platform)
            keyboard = await kClass.createInlineKeyboars()

            for _, secret, chat_name in chats:
                callback = f"start_chat|{secret}"
                await kClass.addCallbackButton(keyboard, chat_name, callback)
            last_id = chats[-1][0]
            callback = f"next_page|{last_id}"
            await kClass.addCallbackButton(keyboard, "Следующие", callback)
            await kClass.adjust(keyboard)

            return await kClass.returnKeyboard(keyboard)
        return None