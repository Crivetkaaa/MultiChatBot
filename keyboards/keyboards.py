from .keyboardsMAX import KeyboardsMAX
from .keyboardsTG import KeybordsTG
from .keyboardsVK import KeyboardsVK
from .baseKeyboards import BaseKeyboards
from config import max_keyboards_len


keyboards = {
    "vk": KeyboardsVK,
    "tg": KeybordsTG,
    "mx": KeyboardsMAX,
}

async def _getKeyboards(platform: str) -> BaseKeyboards:
    return keyboards[platform]

async def userChats(chats, platform, first=True, have_next=False):
    if chats:
        keyboard_class = await _getKeyboards(platform)
        keyboard = await keyboard_class.createInlineKeyboars()

        for _, secret, chat_name in chats:
            callback = f"start_chat|{secret}"
            await keyboard_class.addCallbackButton(keyboard, chat_name, callback)
        last_id = chats[-1][0]
        callback = f"next_page|{last_id}"
        if not( len(chats)<max_keyboards_len) and have_next:
            await keyboard_class.addCallbackButton(keyboard, "Следующие", callback)
        if not first:
            first_id = chats[0][0]
            callback = f"back_page|{first_id}"
            await keyboard_class.addCallbackButton(keyboard, "Назад", callback)
        await keyboard_class.adjust(keyboard)

        return await keyboard_class.returnKeyboard(keyboard)
    
    return None