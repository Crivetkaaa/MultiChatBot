from vkbottle import Keyboard, Callback
from .baseKeyboards import BaseKeyboards

class KeyboardsVK(BaseKeyboards):
    @staticmethod
    async def createInlineKeyboars() -> Keyboard:
        return Keyboard(inline=True)

    @staticmethod
    async def addCallbackButton(kb: Keyboard, text: str, callback: str) -> None:
        kb.add(Callback(text, payload={"cmd": callback}))
        kb.row()

    @staticmethod
    async def adjust(kb: Keyboard, button: int = 1):
        pass

    @staticmethod
    async def returnKeyboard(kb: Keyboard):
        return kb