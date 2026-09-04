from abc import ABC, abstractmethod

class BaseKeyboards(ABC):

    @staticmethod
    @abstractmethod
    async def createInlineKeyboars():
        ...
    @staticmethod
    @abstractmethod
    async def addCallbackButton(kb, text: str, callback: str) -> None:
        ...

    @staticmethod
    @abstractmethod
    async def adjust(kb, button: int = 1) -> None:
        ...

    @staticmethod
    @abstractmethod
    async def returnKeyboard(kb):
        ...