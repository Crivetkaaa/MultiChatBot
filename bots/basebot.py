from classes.user import User
from resours import texts
from services.services_config import Manager
from utils.utils import Utils
import keyboards.keyboards as Keyboards
from database.database import db
from config import max_keyboards_len


class BaseBot:
    @staticmethod
    async def start_handler(usr: User):
        text = texts["help"] + "\n\n" + f'{texts["start_bottom"]} \n{usr.secret}'
        await Manager.info_for_user(usr, text)

    @staticmethod
    async def status_handler(usr:User):
        if usr.in_message:
            await Manager.info_for_user(usr, f'{texts["status"]} \n{usr.who_secret}')
        else:
            await Manager.info_for_user(usr, texts["not_in_chat"])

    @staticmethod
    async def message_handler(usr: User, 
                              secret: str = None, 
                              chat_name:str=None,
                              full_name:str=None,
                              url:str=None,
                              mes:str=None):
        if usr.in_message:
            await Manager.info_for_user(usr, texts["err_new_chat"])
            return
        
        if not secret:
            await Manager.info_for_user(usr, texts["empty_secret"])
            return

        res = await Utils.check_secret(secret)
        if not res:
            await Manager.info_for_user(usr, texts["err_secret"])
            return
        
        await usr.start_chat(secret, full_name, url, mes)
        await Manager.info_for_user(usr, texts["start_chat"])

        if chat_name:
            await usr.addChat(chat_name)

    @staticmethod
    async def quit_handler(usr: User, last_id: int=0, first=True):
        chats = await db.getChats(usr.secret, last_id)
        keyboard = await Keyboards.userChats(chats, usr.user_mes, first)
        if usr.in_message:
            await usr.end_chat()
            await Manager.info_for_user(usr, texts["end_chat"], keyboard)
        else:
            await Manager.info_for_user(usr, texts["not_in_chat"], keyboard)

    @staticmethod
    async def help_handler(usr: User):
        await Manager.info_for_user(usr, texts["help"])

    @staticmethod
    async def callback_handler(usr: User, raw_command: str, full_name: str, url: str, mes: str):
        split_command = raw_command.split("|")
        match split_command[0]:
            case "start_chat":
                who_secret = split_command[1]
                await BaseBot.message_handler(usr, who_secret, None, full_name, url, mes)

            case "next_page":
                last_id = split_command[1]
                await BaseBot.quit_handler(usr, last_id, False)

            case "back_page":
                first_id = int(split_command[1]) - max_keyboards_len-1
                await BaseBot.quit_handler(usr, first_id, False)
            case _:
                await Manager.info_for_user(usr, "err")
            