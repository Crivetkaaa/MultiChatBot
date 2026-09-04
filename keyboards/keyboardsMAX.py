from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types.attachments.buttons.callback_button import CallbackButton

class KeyboardsMAX:
	@staticmethod
	async def userChats(chats):
		builder = InlineKeyboardBuilder()

		for secret, chat_name in chats:
			callback = f"start_chat|{secret}"
			builder.row(CallbackButton(text=chat_name, payload=callback))
		builder.adjust(1)
		return builder.as_markup()