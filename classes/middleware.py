import asyncio
from typing import Any, Awaitable, Callable, Dict, List
from aiogram import BaseMiddleware
from aiogram.types import Message

class AlbumMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.album_cache: Dict[str, List[Message]] = {}
        self.lock = asyncio.Lock()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Если это текст или одиночный файл — пропускаем мгновенно за 0 сек!
        if event.media_group_id is None:
            return await handler(event, data)

        async with self.lock:
            # Если это первый элемент альбома — инициализируем список
            if event.media_group_id not in self.album_cache:
                self.album_cache[event.media_group_id] = []
            
            self.album_cache[event.media_group_id].append(event)

        # Даем микро-паузу для переключения контекста, чтобы долетели остальные части
        await asyncio.sleep(0.05)

        async with self.lock:
            # Если этот элемент больше не в кэше (уже обработан основным хэндлером)
            if event.media_group_id not in self.album_cache:
                return None
                
            # Проверяем, является ли текущее сообщение ПОСЛЕДНИМ пришедшим в кэш на данный момент
            if self.album_cache[event.media_group_id][-1] != event:
                return None

            # Если мы дошли сюда — значит, поток сообщений иссяк и мы собрали абсолютно ВСЕ файлы
            data["album"] = self.album_cache.pop(event.media_group_id)
        
        return await handler(event, data)
