from fastapi import FastAPI, HTTPException
from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChat
from dotenv import load_dotenv
import os
from pprint import pprint
import postgreWork
from chat import GPT
# from workFlask import send_message
import random
import time

load_dotenv()
# Замените значения ниже на ваши
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

gpt = GPT()
app = FastAPI()
client = TelegramClient('session_name_i_own_zergo', API_ID, API_HASH, system_version="4.16.32-vxCUSTOM", device_model='FastAPI Galaxy S24 Ultra, running Android 14')
client.start()

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

@app.post('/task/start/{taskID}')
async def start_task(taskID: int):
    calls = postgreWork.get_all_calls_for_task(taskID)
    statusTask = postgreWork.get_status_task(taskID)
    
    if statusTask == 'processing':
        return 'Task is already in progress'
    
    postgreWork.update_status_task(taskID, 'processing')
    promt = postgreWork.get_promt_task(taskID)

    for call in calls:
        statusTask = postgreWork.get_status_task(taskID)
        if statusTask == 'stop':
            break

        messages = postgreWork.get_last_messages_for_user(call.user_id, count=10)
        allMessages = ''.join(message.text + '\n' for message in messages)
        
        messagesList = [{"role": "user", "content": allMessages}]
        answerGPT = gpt.answer(system=promt, topic=messagesList)
        
        send_message(call.user_id, answerGPT, taskID)
        time.sleep(random.randint(60, 90))
        
    postgreWork.update_status_task(taskID, 'done')
    return {'detail': 'Task done'}

@app.post('/task/stop/{taskID}')
async def stop_task(taskID: int):
    postgreWork.update_status_task(taskID, 'stop')
    return {'detail': 'Task stopped'}

@app.post('/first-contact/start/{taskID}')
async def first_contact(taskID: int):
    calls = postgreWork.get_all_calls_for_task(taskID)
    taskStatus = postgreWork.get_status_task(taskID)
    
    if taskStatus == 'processing':
        return 'Task is already in progress'
    
    postgreWork.update_status_task(taskID, 'processing')
    firstMessage = postgreWork.get_first_message_task(taskID)
    
    for call in calls:
        taskStatus = postgreWork.get_status_task(taskID)
        if taskStatus == 'stop':
            break
        send_message(call.user_id, firstMessage, taskID)
        postgreWork.update_call_is_first_message(call.id, True)
        time.sleep(random.randint(60, 90))
    
    postgreWork.update_status_task(taskID, 'done')
    return {'detail': 'First contact done'}

@app.post('/first-contact/stop/{taskID}')
async def stop_first_contact(taskID: int):
    postgreWork.update_status_task(taskID, 'stop')
    return {'detail': 'First contact stopped'}

@app.post('/create-call/{taskID}')
async def create_call(taskID: int):
    users = postgreWork.get_all_users_for_task(taskID)
    for user in users:
        postgreWork.add_call(userID=user.id, groupID=taskID)
    
    return {'detail': 'Calls created'}

@app.post('/webhook')
async def webhook():
    return {'detail': 'Webhook endpoint'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5002)