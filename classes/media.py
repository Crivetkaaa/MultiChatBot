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