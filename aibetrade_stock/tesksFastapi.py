from fastapi import FastAPI, HTTPException
from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChat
from dotenv import load_dotenv
import os
from pprint import pprint
import postgreWork
from chat import GPT
from workFlask import send_message
import random
import time

load_dotenv()
# Замените значения ниже на ваши
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

gpt = GPT()
app = FastAPI()

@app.post('/task/start/{taskID}')
async def start_task(taskID: int):
    calls = postgreWork.get_all_calls_for_task(taskID)
    statusTask = postgreWork.get_status_task(taskID)
    
    if statusTask == 'processing':
        raise HTTPException(status_code=400, detail='Task is already in progress')
    
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
        raise HTTPException(status_code=400, detail='Task is already in progress')
    
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
        postgreWork.add_call(user_id=user.id, groupID=taskID)
    
    return {'detail': 'Calls created'}

@app.post('/webhook')
async def webhook():
    return {'detail': 'Webhook endpoint'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5002)
