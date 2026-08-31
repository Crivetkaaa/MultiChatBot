from vkbottle import Keyboard, Callback

class KeyboardsVK:

    @staticmethod
    async def userChats(chats):
        keyboard = Keyboard(inline=True)
        for secret, chat_name in chats:
            callback = f"start_chat|{secret}"
            
            # Pass the Text object inside keyboard.add()
            keyboard.add(Callback(chat_name, payload={"cmd": callback}))
            keyboard.row()

        return keyboard
