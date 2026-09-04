from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types.attachments.buttons.callback_button import CallbackButton
from maxapi.types.attachments import AttachmentButton
from .baseKeyboards import BaseKeyboards

class KeyboardsMAX(BaseKeyboards):
	@staticmethod
	async def createInlineKeyboars() -> InlineKeyboardBuilder:
		return InlineKeyboardBuilder()

	@staticmethod
	async def addCallbackButton(kb: InlineKeyboardBuilder, text: str, callback: str) -> None:
		kb.add(CallbackButton(text=text, payload=callback))

	@staticmethod
	async def adjust(kb:InlineKeyboardBuilder, button:int = 1):
		kb.adjust(button)

	@staticmethod
	async def returnKeyboard(kb: InlineKeyboardBuilder) -> AttachmentButton:
		return kb.as_markup()