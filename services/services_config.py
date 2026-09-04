from .service_manager import ServiceManager
from .vk import VkService
from .tg import TgService
from .max import MxService

from config import vk_bot, tg_bot, mx_bot

bot_configs = [
    (VkService, vk_bot),
    (TgService, tg_bot),
    (MxService, mx_bot),
]

services = [service_class(bot) for service_class, bot in bot_configs]
Manager = ServiceManager(*services)