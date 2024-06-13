from flask import Flask, request, jsonify
from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChat
from dotenv import load_dotenv
import os 
from pprint import pprint
import requests
load_dotenv()
# Замените значения ниже на ваши
API_ID =os.getenv('API_ID') 
API_HASH = os.getenv('API_HASH')
TOKEN_BOT = os.getenv('TOKEN_BOT_EVENT')
# PHONE_NUMBER = 'your_phone_number'
# CHANNEL_ID = 'your_channel_id'
# CHAT_ID = 'your_chat_id'


app = Flask(__name__)

# Создаем Telegram клиент
client = TelegramClient('session_name2', API_ID, API_HASH, system_version="4.16.32-vxCUSTOM", device_model='Flask Galaxy S24 Ultra, running Android 14')
client.start()


# client = TelegramClient('session_name_flask', API_ID, API_HASH, system_version="4.16.32-vxCUSTOM", device_model='Flask Galaxy S24 Ultra, running Android 14')
# client.suo
# Функция для отправки сообщения в Telegram
def split_text(text, max_length):
    """
    Split the text into chunks of maximum length.
    
    Args:
        text (str): The text to split.
        max_length (int): The maximum length of each chunk.

    Returns:
        list: A list of chunks of the text.
    """
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + max_length])
        start += max_length
    return chunks

    # Пример     использования функции:

        
def send_message(chatID, message, threadID=None):
    # client.send_message(entity=chatID, message=message, message_thread_id=threadID)
    # client.send_message(entity=-2118909508, message=message, message_thread_id=4294967329)
# https://t.me/+tMRqqjOo2BplZGM6
# https://t.me/+tMRqqjOo2BplZGM6
# https://t.me/c/2118909508/33
    # text = "Это очень большой текст, который нужно разбить на несколько частей, чтобы отправить его в Telegram."
    max_length = 3000  # Максимальная длина сообщения в Telegram
    chunks = split_text(text=message, max_length=max_length)
    for chunk in chunks:
        # client.send_message(entity=chatID, message=message)#work
        client.send_message(entity=chatID, message=chunk)#work
    # client(SendMessageRequest(2118909508, 'hello', send_as='4294967329'))
    # client.send_message(InputPeerChat(1087968824), 'hi')
    # a=client.get_entity(1087968824) 
    # a=client.get_entity('https://t.me/+tMRqqjOo2BplZGM6')
    # pprint(a)
    # client.send
    # https://t.me/c/2118909508/33
    # send_message('id чата или ссылка', 'Cамо сообщение', reply_to = "идентификатор группы в чате")
    # destination_group_invite_link=4294967329
    # entity=client.get_entity(destination_group_invite_link)
    # client.get_input_entity(-2118909508)
    
    # client.send_message(entity=entity,message="Hi")
    # client.se
# Обработчик вебхука
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    chenalID = data.get('channel_id')
    message = data.get('message')
    chatID=data.get('chat_id')
    # Проверяем, что пришло корректное сообщение
    if chenalID and message:
        # Если идентификатор канала совпадает с ожидаемым, отправляем сообщение в Telegram
        # if channel_id == CHANNEL_ID:
        send_message(chatID, message, chenalID)
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Missing channel ID or message'}), 400
    
def check_user_in_chat(user_id, chat_id):
        url = f'https://api.telegram.org/bot{TOKEN_BOT}/getChatMember'
        params = {
            'chat_id': chat_id,
            'user_id': user_id
        }
        response = requests.get(url, params=params)
        data = response.json()
        pprint(data)
        if data['ok']:
            status = data['result']['status']
            if status in ['member', 'administrator', 'creator']:
                return True
            else:
                return False
        else:
            return False
        
@app.route('/check-members/<int:chat_id>/<int:user_id>', methods=['GET'])
def check_members(chat_id, user_id):
    # Получаем список участников канала
    

    TOKEN = 'YOUR_BOT_TOKEN'
    CHAT_ID = 'your_chat_id'  # ID группы или супергруппы
    USER_ID = 'user_id_to_check'

    

    is_in_chat = check_user_in_chat(chat_id, chat_id)
    return is_in_chat
#     new_func(is_in_chat)

# def new_func(is_in_chat):
#     if is_in_chat:
#         print("User is a member of the chat.")
#     else:
#         print("User is not a member of the chat.")


if __name__ == '__main__':
    pass
    # send_message(2118909508, 'Cамо сообщение', 33 )
    # app.run(host='0.0.0.0', port='5002', debug=False)
