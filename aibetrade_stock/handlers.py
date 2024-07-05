import asyncio
from aiogram import types, F, Router, html, Bot
from aiogram.types import (Message, CallbackQuery,
                           InputFile, FSInputFile,
                            MessageEntity, InputMediaDocument,
                            InputMediaPhoto, InputMediaVideo, Document)
from aiogram.filters import Command, StateFilter,ChatMemberUpdatedFilter
from aiogram.types.message import ContentType
from pprint import pprint
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Any, Dict
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER

from aiogram.types import ChatMemberUpdated
# from aiogram.dispatcher.filters import ChatMemberUpdatedFilter
# from helper import (get_all_user_list, get_dates, 
#                     timestamp_to_date, time_epoch,
#                     get_future_events, prepare_message_event,
#                     get_today_pracktik,prepare_message_pracktik,
#                     langList, langListKeybord, typeFiles)
# # from createKeyboard import *
# from payments import *
from dotenv import load_dotenv
import os
# from chat import GPT
import postgreWork 
# import chromaDBwork
from loguru import logger
# from workRedis import *
# from calendarCreate import create_calendar
# from helper import create_db,convert_text_to_variables,create_db2,get_next_weekend,find_and_format_date,find_patterns_date,create_db_for_user
from datetime import datetime,timedelta
# from workGS import Sheet
import uuid
import time
# import speech_recognition as sr
# from promt import clasificatorPromt

load_dotenv()
TOKEN = os.getenv('TOKEN_BOT_EVENT')
# PAYMENTS_TOKEN = os.getenv('PAYMENTS_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK')
SECRECT_KEY = os.getenv('SECRET_CHAT')

# sql = Ydb()

router = Router()

bot = Bot(token=TOKEN,)

import requests
import hashlib
import base64
import json
import hmac
# import loguru
from loguru import logger
logger.add("file_{time}.log",format="{time} - {level} - {message}", rotation="100 MB", retention="10 days", level="DEBUG")
# Define the secret key and other required information

# task_code = "sub"
# user_id = "your_telegram_user_id"
# action = True  # or False depending on your requirement

# Prepare the body of the request


# Define the headers
# headers = {
#     "Content-Type": "application/json",
#     "X-Api-Signature-Sha256": signature
# }

# Define the URL
# url = "https://gql.aibetrade.com/hook/task"

# Make the POST request
# response = requests.post(url, headers=headers, data=body_json)

# # Print the response
# print("Status Code:", response.status_code)
# print("Response Body:", response.json())
def request_AiBeTrade(body, webhook:str=WEBHOOK_URL):
    # body = {
    # "code": task_code,
    # "userId": user_id,
    # "action": action
    # }
    secret_key = SECRECT_KEY

    # Convert the body to a JSON string
    body_json = json.dumps(body)
    total_params = body_json
    # print(total_params)
    total_params = total_params.encode('utf-8')
    secret_key = secret_key.encode('utf-8')
    
    # Create the signature
    # signature = base64.b64encode(hashlib.sha256((body_json + secret_key).encode()).digest()).decode()
    signature = hmac.new(secret_key, total_params, hashlib.sha256).hexdigest()
    # print(signature)
    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "X-Api-Signature-Sha256": signature
    }

    # Define the URL
    url=WEBHOOK_URL
    # pprint(headers)
    # pprint(body_json)
    # Make the POST request

    logger.debug(f'{url=}\n')
    logger.debug(f'{headers=}\n')
    logger.debug(f'{body_json=}\n')
    response = requests.post(url, headers=headers, data=body_json)  
    logger.debug(f'{response.text=}\n')
    # pprint(response.text)  



@router.message(Command("help"))
async def help_handler(msg: Message, state: FSMContext):
    mess="/start - начало работы"
    await msg.answer(mess)
    return 0

@router.message_reaction()
async def message_reaction(msg: Message):
    pprint(msg)
    return 0

#Обработка калбеков
@router.callback_query()
async def message(msg: CallbackQuery):
    pprint(msg.message.message_id)
    userID = msg.from_user.id
    await msg.answer()
    callData = msg.data
    # pprint(callData)
    logger.debug(f'{callData=}')

           
    return 0


# # @router.message(F.voice)
# @router.message(F.left_chat_member)
# async def left_chat_member(msg: Message, state: FSMContext):
#     print('left_chat_member')
#     print(msg)
#     # await message(msg1, state)  
#     pass
# @router.message(F.join_chat_member)
# async def join_chat_member(msg: Message, state: FSMContext):
#     print('join_chat_member')
#     print(msg)
#     # await message(msg1, state)  
    
#     pass

@router.chat_boost()
async def chat_boost_handler(chat_boost: types.ChatBoostUpdated) -> Any: 
    
    print(f'{"booost":_^34}')
    pprint(chat_boost.__dict__)
    print(f'{"chat":_^34}')
    pprint(chat_boost.chat.__dict__)

    userID=chat_boost.boost.source.user.id
    chatID=chat_boost.chat.id
    print(f"{chatID=}")
    print(f"{userID=}")

    task_code = f"boost{chatID}"
    action = True
    body={
        "code": task_code,
        "userId": userID,
        "action": action
    }
    pprint(body)
    request_AiBeTrade(body)
    pass

@router.removed_chat_boost()
async def removed_chat_boost_handler(chat_boost: types.ChatBoostRemoved) -> Any: 
    # pprint(chat_boost.__dict__)
    # pprint(chat_boost.chat.__dict__)
    print(f'{"booost":_^34}')
    pprint(chat_boost.__dict__)
    print(f'{"chat":_^34}')
    pprint(chat_boost.chat.__dict__)

    # pprint(chat_boost.source.__dict__)
    userID=chat_boost.source.user.id
    chatID=chat_boost.chat.id
    print(f"{chatID=}")
    print(f"{userID=}")

    task_code = f"boost{chatID}"
    action = False
    body={
        "code": task_code,
        "userId": userID,
        "action": action
    }
    pprint(body)
    request_AiBeTrade(body)
    pass

@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(event: ChatMemberUpdated):
    print('on_user_leave')
    # pprint(event)
    # print(event.from_user.id)
    userID=event.from_user.id
    chatID=event.chat.id
    # print(chatID)
    task_code = f"sub{chatID}"
    action = False
    body={
        "code": task_code,
        "userId": userID,
        "action": action
    }
    # pprint(body)
    request_AiBeTrade(body)

@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated):
    # await message(event.message, event.state)  
    print('on_user_join')
    # pprint(event)
    # print(event.from_user.id)
    userID=event.from_user.id
    chatID=event.chat.id
    task_code = f"sub{chatID}"
    action = True
    body={
        "code": task_code,
        "userId": userID,
        "action": action
    }
    # pprint(body)
    request_AiBeTrade(body)
    
    # print(chatID)
    pass

async def delete_and_send_message(msg:Message, text='You have violated the rules of this chat.  Message deleted. If you violate it again, you will be blocked.'):
    """удаление сообщения и отправка нового сообщения"""
    await msg.delete()
    new_msg = await msg.answer(text,)
    # делайем слип (асинхронно)
    await asyncio.sleep(5)
    # на всякий случай проверяем есть ли еще сообщение
    try:
        print('удалили')
        await new_msg.delete()
    except Exception as e:
        pprint(e)
        pass
    pass

# aibetradecombot/app?startapp

# office.aibetrade.com/?ref

def check_ref(msg:Message):
    """Проверка на реферальную ссылку true если его нету"""
    text=msg.text
    # Проверяем наличие http или t.me/
    if 'http' in text or 't.me/' in text:
        # Проверяем отсутствие aibetrade
        if 'aibetrade' not in text:
            return True
        else:
            return False
    return False

def chek_http(msg):
    text=msg.text
    if text in 'http':
        return True
    return False

    

    pass
#Обработка сообщений
@router.message()
async def message(msg: Message, state: FSMContext):
    # pprint(msg.__dict__)
    # 241 реф ссылки #240
    userID = msg.from_user.id
    # print(msg.chat.id)
    print(f"{msg.chat.id=}")
    print(f'{userID=}')
    
    
    # if msg.chat.id != -1002118909508:
    #     return 0
    if msg.chat.id not in [-1002118909508,-1002242862285,-1002231035352,-1002163616957]:
        return 0
    
    thereadID=msg.message_thread_id
    # print(f"{thereadID=}")
    # print(thereadID)
    # print(f"{msg.text.find('aibetrade')=}")  
    # print(f"{msg.text.find('http')=}")
    # print(f"{msg.text.find('t.me/')=}")
    

    #336464992 I OWN ZERGO
    if userID in [327475194,336464992, 1087968824]: return 0
    
    
    if check_ref(msg):
        print(f"{'попали в чек':_^34}")
        print(f"{msg.chat.id=}")
        print(f'{userID=}')

        # if check_ref(msg) == False: await 
        if thereadID==240 or thereadID==241:            
            # print('попали')
            await delete_and_send_message(msg)    
            return 0
        else:
            # print('не попали')
            if msg.chat.id == -1002118909508:
                await delete_and_send_message(msg, text='You have violated the rules of this group.  Referral links can be published in the "Referral links" threads')
            else:
                await delete_and_send_message(msg)
            return 0
    else:
        
        # print('попали')
        # await delete_and_send_message(msg)
        return 0

    print(thereadID)

    pass



if __name__ == '__main__':
    body={
        "code": 'boost-1001609461642',
        "userId": 327475194,
        "action": True  
    }
    pprint(body)
    request_AiBeTrade(body)

    pass
