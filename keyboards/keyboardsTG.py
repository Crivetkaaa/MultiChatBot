from aiogram.utils.keyboard import InlineKeyboardBuilder
from .baseKeyboards import BaseKeyboards

class KeybordsTG(BaseKeyboards):
    @staticmethod
    async def createInlineKeyboars() -> InlineKeyboardBuilder:
        return InlineKeyboardBuilder()
    
    @staticmethod
    async def addCallbackButton(kb: InlineKeyboardBuilder, text: str, callback: str) -> InlineKeyboardBuilder:
        kb.button(text=text, callback_data=callback)

    @staticmethod
    async def adjust(kb:InlineKeyboardBuilder, button:int = 1):
        kb.adjust(button)

    @staticmethod
    async def returnKeyboard(kb: InlineKeyboardBuilder):
        return kb.as_markup()
