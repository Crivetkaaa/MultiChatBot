from enum import Enum
from dataclasses import dataclass

@dataclass
class Media:
    m_type: str
    filename: str
    m_bytes: bytes

class MediaType(Enum):
    PHOTO = "photo"
    VIDEO = 'video'
    DOCUMENT = 'doc'


@dataclass
class Sticker:
    s_type: str
    filename: str
    m_bytes: bytes
    
class StickerType(Enum):
    VIDEO = "webm"
    PHOTO = "webp"