from telethon import TelegramClient, events
from chat import GPT
from pprint import pprint
# from helper import check_pattern_count,convert_text_to_variables
from datetime import datetime
from dotenv import load_dotenv
import time
import random
load_dotenv()
import os
import base64
import postgreWork
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.tl.functions.channels import GetFullChannelRequest
import asyncio
from helper import abt_serch
from workRedis import clear_history, add_message_to_history, get_history
# Вставьте ваши данные для подключения к Telegram API
# api_id = 'YOUR_API_ID'
# api_hash = 'YOUR_API_HASH'
API_ID =os.getenv('API_ID') 
API_HASH = os.getenv('API_HASH')
# phone_number = 'YOUR_PHONE_NUMBER'
gpt=GPT()
# Создайте экземпляр клиента Telegram
client = TelegramClient(session='session_name_i_own_zergo', api_id=API_ID, api_hash=API_HASH, system_version="4.16.32-vxCUSTOM", device_model='FastAPI Galaxy S24 Ultra, running Android 14')


# Авторизуйтесь в клиенте
client.start()

chenalName = [-1001442825795,400923372] 

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

async def message_me(text:str, userID):
    """Обработака сообщений от меня"""
    # text=msg.text
    print('-'*30)
    print(f'{text=}')
    # pprint(text)
    admins=[327475194,6984701819,400923372]
    if userID not in admins:
        return None
    
    comand=abt_serch(text)
    print(f'{comand=}')
    # if userID != 327475194 or userID != 6984701819:
    
    
    if comand=='Invalid command.':
        return None
    
    else:
        print(f'отправили сообщение  {comand=}')
        await client.send_message(userID, message=str(comand))
        return comand
@client.on(events.NewMessage())
async def new_message_listener(event):
    # Обработка новых сообщений
    userID=event.message.sender_id
    text=event.message.text

    userInCalls=postgreWork.check_user_in_call(userID)
    
    if not userInCalls: return 0
    
    Call_User=postgreWork.get_call_user(userID)
    
    if not Call_User.is_dialog:
        postgreWork.update_call_is_dialog(userID, True)

    # postgreWork.check_user(userID)
    
    
    
    chatID=event.peer_id.__dict__
    # if chatID['channel_id']:
    # pprint(chatID)
    # print('peer_id')
    my_chat= ''
    print(f'{userID=}')
    print(f'{chatID=}')
    print(f'{text=}')
    # if await message_me(text=text,userID=userID) is not None: #все сообщения от меня обрабатыаются в  message_me а none значит что это не мое сообщение
    #     return 0
    
    #TODO если call is_first_message==True и эт пользователь то ведем диалог с ним
    match event.peer_id.__dict__:

        case {'channel_id': chatID}:
            chatID=chatID
            typeChat='chenal'
            # my_chat= await client.get_entity(PeerChannel(chatID))
            return 0
        case {'chat_id': chatID}:
            chatID=chatID
            typeChat='group'
            # my_chat= await client.get_entity(PeerChat(chatID))
            return 0

        case {'user_id': chatID}:
            chatID=chatID
            typeChat='user'
        
        case _:
            print('error')
            pprint(event.peer_id.__dict__)
            typeChat='error'
            
    
    # pprint(event.peer_id.__dict__)
    message_id=event.message.id
    print(f'{userID=}')
    print(f'{chatID=}')
    print(f'{message_id=}')
    print(f'{text=}')
    print(f'{typeChat=}')


    postgreWork.add_call_message(message_id, chatID, userID, text, typeChat)
    if typeChat=='error':
        return 0
    
    #group_id=taskID
    Task=postgreWork.get_task(Call_User.group_id)
    promt=gpt.load_prompt(Task.url)

    history=get_history(chatID)
    if len(history) > 4:
        clear_history(userID)
        
    add_message_to_history(userID, 'user', text)

    history = get_history(userID) 
    
    # messagesList = [
    #   {"role": "user", "content": text}
    #   ]
    
    # answer, allToken, allPrice = gpt.answer('',messagesList,1)
    # await event.reply(answer)  
    # else:
    answer, allToken, allPrice = gpt.answer(promt,history,1)
    await client.send_message(userID, message=answer)
        
    postgreWork.add_call_message(Call_User.group_id, userID, message_id, answer, typeChat,type_chat='system', )
    # await client.send_message(6984701819, message=f"Всего токенов потрачено:{allToken}\nЦена: {allPrice}")
    add_message_to_history(userID, 'system', answer)
    #chenalID записывается без -100 в начале -1002010911633

# Запустите прослушивание новых сообщений
def main():
    
    print('[OK]')
  
    client.run_until_disconnected()


if __name__ == '__main__':

    main()
    
