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


# Вставьте ваши данные для подключения к Telegram API
# api_id = 'YOUR_API_ID'
# api_hash = 'YOUR_API_HASH'
api_id =os.getenv('API_ID') 
api_hash = os.getenv('API_HASH')
# phone_number = 'YOUR_PHONE_NUMBER'
gpt=GPT()
# Создайте экземпляр клиента Telegram
client = TelegramClient('session_name', api_id, api_hash, system_version="4.16.30-vxCUSTOM", device_model='Samsung Galaxy S24 Ultra, running Android 14')


# Авторизуйтесь в клиенте
client.start()
# promt="""Преобразуй сообщение в следующую структуру:
# {Название портфеля без ковычек}, {Название акции только на латинице без русских названий}, {Тип сигнала: BUY или SELL},{Цена акции},{Процент остатка акции в портфеле без знака процент}. Структура должна включать в себя разделители данных в виде {} и между разделителями данных не должно быть пробелов"""
# Определите список идентификаторов каналов, из которых вы хотите получать сообщения
# channel_ids = [-1001281274611, -1001747110091,-1001117865178,'SwiftBook','Герасимова и Игорь Новый','-1002010911633',-1002010911633]  # Замените на реальные идентификаторы каналов
#см Разработка бота Афиша/ tg источники
chenalName = [-1001442825795,400923372] 
# @client.on(events.NewMessage())
# @client.on(events.NewMessage(chats=lambda x: x in chenalName))
#@client.on(events.NewMessage(chats=chenalName))
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
@client.on(events.NewMessage())
async def new_message_listener(event):
    # Обработка новых сообщений
    userID=event.message.sender_id
    text=event.message.text
    # pprint(event.__dict__)

    pprint(event.message.__dict__)
    # pprint(event.__dict__['_input_chat'].__dict__)
    print('from_id') #caat
    pprint(event.from_id.__dict__)
    # pprint(event.__dict__['_chat_peer'].__dict__)
    chatID=event.peer_id.__dict__['channel_id']
    message_id=event.message.id
    print(f'{userID=}')
    print(f'{chatID=}')
    print(f'{message_id=}')
    print(f'{text=}')

    
    if text.find('#gpt') != -1:
        1+0
        #await event.reply('Some text') 
        # отправляем в gpt
    
    elif text.find('push') == -1:
        return 0
    
    
    messagesList = [
      {"role": "user", "content": text}
      ]
    url='https://docs.google.com/document/d/16KdZVK4a_QiM7wmMCmV-42XX9dB9FtsmNvYj4NCAJ7o/edit?usp=sharing'
    promt=gpt.load_prompt(url)
    
    # dateNow = datetime.now().strftime("%d.%m.%Y %A")
    time.sleep(random.randint(5, 20))
    # promt=promt.replace('[dateNow]',dateNow)
    
    if text.find('#gpt') != -1:
        # if text.startswith('/image'):
        #     text = text.replace('/image ', '').replace('#gpt','')

        #     url = gpt.create_image(promt=text)
        #     client.send_file(event.chat.id, url)
        #     return 0
        
        # pprint(event.__dict__)
        # pprint(event.message.__dict__)
        if event.message.media:
            pprint(event.message.media.__dict__)
            # pprint(event.message.__dict__)
        # Получаем информацию о самом большом изображении
            photo = event.message.media.photo
            pprint(photo.__dict__)
            path=f'{userID}.jpg'
            await client.download_media(event.message, file=path)
            
            base64_image = encode_image(path)

          
            # Получаем файл изображения
            # file = await client.download_media(photo)
            
            # Отправляем изображение на распознавание с помощью OpenAI
            # with open(file, 'rb') as f:
            #     image_data = f.read()     
            
            answer = gpt.vision_answer(text,base64_image)
            await event.reply(answer)
            os.remove(path)

        else:
            answer, allToken, allPrice = gpt.answer('',messagesList,1)
            await event.reply(answer)  
    else:
        answer, allToken, allPrice = gpt.answer(promt,messagesList,1)
        await client.send_message(6984701819, message=answer)
        

    # await client.send_message(6984701819, message=f"Всего токенов потрачено:{allToken}\nЦена: {allPrice}")

    #chenalID записывается без -100 в начале -1002010911633

# Запустите прослушивание новых сообщений
def main():
    
    print('[OK]')
    
    client.run_until_disconnected()
    print('Подключение разорвано')

if __name__ == '__main__':
    
    main()
        # print('Подключение потеряно, переподключение...')
