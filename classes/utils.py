from .media import MediaType, Media, Sticker, StickerType
import subprocess
from functools import wraps

class Utils:
    @staticmethod
    async def webm_to_gif(m_bytes: bytes) -> bytes:
        result = subprocess.run(
        [
            "ffmpeg",
            "-i", "pipe:0",
            "-vf", "fps=15,scale=512:-1:flags=lanczos",
            "-f", "gif",
            "pipe:1"
        ],
            input=m_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        return result.stdout

    @staticmethod
    async def check_secret(secret: str) -> bool:
        if len(secret) != 69:
            return False
        return True

    @staticmethod
    async def createMedia(media_type: MediaType, filename: str, m_bytes:bytes) -> Media:
        return Media(
            media_type, filename, m_bytes
        )

    @staticmethod
    async def createSticker(sticker_type: StickerType, filename: str, s_bytes: bytes) -> Sticker:
        return Sticker(
            sticker_type, filename, s_bytes
        )
    
    @staticmethod
    def split_text(func):
        @wraps(func)
        def wrapper(text, *args, **kwargs):
            split_t = text.text.split(" ")         
            if len(split_t) > 2:
                split_t = split_t[1:3]
            else:
                split_t = [split_t[-1]]
                
            return func(text, *split_t, *args, **kwargs)
            
        return wrapper
