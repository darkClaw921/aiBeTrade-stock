from flask import Flask, request, jsonify
from telethon import TelegramClient, events, sync
from dotenv import load_dotenv
import os 
load_dotenv
# Замените значения ниже на ваши
API_ID =os.getenv('API_ID') 
API_HASH = os.getenv('API_HASH')

PHONE_NUMBER = 'your_phone_number'
# CHANNEL_ID = 'your_channel_id'
# CHAT_ID = 'your_chat_id'


app = Flask(__name__)

# Создаем Telegram клиент
client = TelegramClient('session_name', API_ID, API_HASH, system_version="4.16.32-vxCUSTOM", device_model='Flask Galaxy S24 Ultra, running Android 14')
client.start()

# Функция для отправки сообщения в Telegram
def send_message(chatID, message):
    client.send_message(chatID, message)

# Обработчик вебхука
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    channel_id = data.get('channel_id')
    message = data.get('message')
    chatID=data.get('chat_id')
    # Проверяем, что пришло корректное сообщение
    if channel_id and message:
        # Если идентификатор канала совпадает с ожидаемым, отправляем сообщение в Telegram
        # if channel_id == CHANNEL_ID:
        send_message(chatID, message)
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Missing channel ID or message'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002', debug=False)
