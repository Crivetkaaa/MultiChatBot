from classes.user import User
from resours import texts
from services.services_config import Manager
import utils as Utils
import keyboards.keyboards as Keyboards
from database.database import db


class BaseBot:
    @staticmethod
    async def start_handler(usr: User):
        text = texts["help"] + "\n\n"
        text_bottom = f'{texts["start_bottom"]} \n{usr.secret}'
        await Manager.info_for_user(usr, text)
        await Manager.info_for_user(usr, text_bottom)

    @staticmethod
    async def status_handler(usr:User):
        if usr.in_message:
            await Manager.info_for_user(usr, f'{texts["status"]} \n{usr.who_secret}')
        else:
            await BaseBot.quit_handler(usr)

    @staticmethod
    async def message_handler(usr: User, 
                              secret: str = None, 
                              chat_name:str=None,
                              event=None,
                              mes:str=None):
        full_name, url = await Utils.getFullName(event)
        
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
    async def create_chats_keyboard(usr: User, last_id: int=0, first=True, next_page=True):
        chats, have_more = await db.getChats(usr.secret, last_id, next_page)
        if next_page:
            have_next = have_more
        else:
            have_next = True
            first = not have_more

        keyboard = await Keyboards.userChats(chats, usr.user_mes, first, have_next)
        return keyboard

    @staticmethod
    async def quit_handler(usr: User, keyboard=None, message_id = 0):    
        keyboard = await BaseBot.create_chats_keyboard(usr)    
        if usr.in_message:
            await usr.end_chat()
            await Manager.info_for_user(usr, texts["end_chat"], keyboard, message_id)
        else:
            await Manager.info_for_user(usr, texts["not_in_chat"], keyboard, message_id)

    @staticmethod
    async def user_not_in_chat(usr):
        keyboard = await BaseBot.create_chats_keyboard(usr)    
        await Manager.info_for_user(usr, texts["not_in_chat"], keyboard)


    @staticmethod
    async def help_handler(usr: User):
        await Manager.info_for_user(usr, texts["help"])

    @staticmethod
    async def callback_handler(usr: User, raw_command: str, event, mes: str):
        split_command = raw_command.split("|")
        match split_command[0]:
            case "start_chat":
                who_secret = split_command[1]
                await BaseBot.message_handler(usr, who_secret, None, event, mes)

            case "next_page":
                last_id = int(split_command[1])
                keyboard = await BaseBot.create_chats_keyboard(usr, last_id, False, True)
                await Manager.info_for_user(usr, texts["not_in_chat"], keyboard, usr.last_message_id)

            case "back_page":
                first_id = int(split_command[1])
                keyboard = await BaseBot.create_chats_keyboard(usr, first_id, False, False)
                await Manager.info_for_user(usr, texts["not_in_chat"], keyboard, usr.last_message_id)

            case "fast_answer":
                who_secret = split_command[1]
                full_name, url = await Utils.getFullName(event)
                await usr.start_chat(who_secret, full_name, url, mes)
                await Manager.info_for_user(usr, texts["start_chat"])

            case _:
                await Manager.info_for_user(usr, "err")
            