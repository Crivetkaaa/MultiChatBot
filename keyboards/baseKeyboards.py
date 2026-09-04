class BaseKeyboards:
    @staticmethod
    async def createInlineKeyboars():
        pass

    @staticmethod
    async def addCallbackButton(kb, text: str, callback: str) -> None:
        pass
    @staticmethod
    async def adjust(kb, button: int = 1) -> None:
        pass

    @staticmethod
    async def returnKeyboard(kb):
        pass