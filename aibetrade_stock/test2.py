from telethon import TelegramClient, events
from chat import GPT
from pprint import pprint
# from helper import check_pattern_count,convert_text_to_variables
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import os


# Вставьте ваши данные для подключения к Telegram API
# api_id = 'YOUR_API_ID'
# api_hash = 'YOUR_API_HASH'
api_id =os.getenv('API_ID') 
api_hash = os.getenv('API_HASH')
# phone_number = 'YOUR_PHONE_NUMBER'
gpt=GPT()
# Создайте экземпляр клиента Telegram
client = TelegramClient('session_name', api_id, api_hash)

# Авторизуйтесь в клиенте
client.start()
promt="""Преобразуй сообщение в следующую структуру:
{Название портфеля без ковычек}, {Название акции только на латинице без русских названий}, {Тип сигнала: BUY или SELL},{Цена акции},{Процент остатка акции в портфеле без знака процент}. Структура должна включать в себя разделители данных в виде {} и между разделителями данных не должно быть пробелов"""
# Определите список идентификаторов каналов, из которых вы хотите получать сообщения
# channel_ids = [-1001281274611, -1001747110091,-1001117865178,'SwiftBook','Герасимова и Игорь Новый','-1002010911633',-1002010911633]  # Замените на реальные идентификаторы каналов
#см Разработка бота Афиша/ tg источники
chenalName = [-1001442825795,] 
# @client.on(events.NewMessage())
# @client.on(events.NewMessage(chats=lambda x: x in chenalName))
@client.on(events.NewMessage(chats=chenalName))
async def new_message_listener(event):
    # Обработка новых сообщений
    
    text=event.message.text
    print(text)
    
    
    if text.find('push') == -1:
        return 0
    
    
    messagesList = [
      {"role": "user", "content": text}
      ]
    # url='https://docs.google.com/document/d/1riRchaMaJC27ikxBx_02W2Z7GANDnFswzTUHy49qaqI/edit?usp=sharing'
    # promt=gpt.load_prompt(url)
    
    dateNow = datetime.now().strftime("%d.%m.%Y %A")
    
    # promt=promt.replace('[dateNow]',dateNow)
    answer, allToken, allPrice = gpt.answer(promt,messagesList,1,'gpt-3.5-turbo-16k')
    await client.send_message(327475194, message=answer)
    await client.send_message(327475194, message=f"Всего токенов потрачено:{allToken}\nЦена: {allPrice}")

    #chenalID записывается без -100 в начале -1002010911633

# Запустите прослушивание новых сообщений
def main():
    
    print('[OK]')
    
    client.run_until_disconnected()
    print('Подключение разорвано')

if __name__ == '__main__':
    
    main()
        # print('Подключение потеряно, переподключение...')
