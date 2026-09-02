from classes.user import User
from resours import texts
from services.service_manager import Manager
from utils.utils import Utils

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
    async def quit_handler(usr: User, keyboard=None):
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
        print(raw_command)
        split_command = raw_command.split("|")
        match split_command[0]:
            case "start_chat":
                who_secret = split_command[1]
                await BaseBot.message_handler(usr, who_secret, None, full_name, url, mes)
            case _:
                await Manager.info_for_user(usr, "err")
            
        


