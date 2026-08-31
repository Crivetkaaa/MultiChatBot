from aiogram.utils.keyboard import InlineKeyboardBuilder

class KeybordsTG:
    @staticmethod
    async def userChats(chats):
        builder = InlineKeyboardBuilder()

        for secret, chat_name in chats:
            callback = f"start_chat|{secret}"
            builder.button(text=chat_name, callback_data=callback)
        builder.adjust(1)

        return builder.as_markup()