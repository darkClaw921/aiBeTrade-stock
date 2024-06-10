import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType, ChatMemberUpdated
# from aiogram.utils import executor
from aiogram.fsm.storage.memory import MemoryStorage
import requests
import os
from dotenv import load_dotenv
load_dotenv()
API_TOKEN = os.getenv('TOKEN_BOT_EVENT')
WEBHOOK_URL = 'YOUR_WEBHOOK_URL'
SERVER_URL = 'YOUR_SERVER_URL'

logging.basicConfig(level=logging.INFO)
print(API_TOKEN)    
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message_handler(content_types=ContentType.NEW_CHAT_MEMBERS)
async def new_member_handler(message: types.Message):
    for new_member in message.new_chat_members:
        data = {
            'event': 'new_member',
            'user_id': new_member.id,
            'username': new_member.username,
            'chat_id': message.chat.id
        }
        requests.post(SERVER_URL, json=data)
        logging.info(f"New member: {new_member.username} (ID: {new_member.id}) joined the chat {message.chat.id}")

@dp.message_handler(content_types=ContentType.LEFT_CHAT_MEMBER)
async def left_member_handler(message: types.Message):
    left_member = message.left_chat_member
    data = {
        'event': 'left_member',
        'user_id': left_member.id,
        'username': left_member.username,
        'chat_id': message.chat.id
    }
    requests.post(SERVER_URL, json=data)
    logging.info(f"Member: {left_member.username} (ID: {left_member.id}) left the chat {message.chat.id}")

@dp.chat_member_handler()
async def chat_member_update_handler(chat_member_update: ChatMemberUpdated):
    if chat_member_update.new_chat_member.status == 'member':
        data = {
            'event': 'new_member',
            'user_id': chat_member_update.new_chat_member.user.id,
            'username': chat_member_update.new_chat_member.user.username,
            'chat_id': chat_member_update.chat.id
        }
        requests.post(SERVER_URL, json=data)
        logging.info(f"New member: {chat_member_update.new_chat_member.user.username} (ID: {chat_member_update.new_chat_member.user.id}) joined the chat {chat_member_update.chat.id}")
    elif chat_member_update.new_chat_member.status == 'left':
        data = {
            'event': 'left_member',
            'user_id': chat_member_update.new_chat_member.user.id,
            'username': chat_member_update.new_chat_member.user.username,
            'chat_id': chat_member_update.chat.id
        }
        requests.post(SERVER_URL, json=data)
        logging.info(f"Member: {chat_member_update.new_chat_member.user.username} (ID: {chat_member_update.new_chat_member.user.id}) left the chat {chat_member_update.chat.id}")

# Placeholder for future reaction events
@dp.message_handler(content_types=ContentType.ANY)
async def reaction_handler(message: types.Message):
    # This is a placeholder for future reaction events
    # Currently, Telegram API does not support reaction events
    pass

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == '__main__':
    # executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
    dp.start_polling(dp)