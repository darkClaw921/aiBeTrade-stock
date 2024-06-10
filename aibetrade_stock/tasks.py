from flask import Flask, request, jsonify
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
API_ID =os.getenv('API_ID') 
API_HASH = os.getenv('API_HASH')


gpt=GPT()
# PHONE_NUMBER = 'your_phone_number'
# CHANNEL_ID = 'your_channel_id'
# CHAT_ID = 'your_chat_id'


app = Flask(__name__) # TASKS для пользователей


@app.route('/task/start/<int:taskID>', methods=['POST'])  
def start_task(taskID):
    calls=postgreWork.get_all_calls_for_task(taskID)
    statusTask=postgreWork.get_status_task(taskID)
    
    if statusTask=='porocessing':
        return 'Task is already in progress'
    
    postgreWork.update_status_task(taskID, 'processing')

    promt=postgreWork.get_promt_task(taskID)
    # firstMessage=postgreWork.get_first_message_task(taskID)

    for call in calls:
        statusTask=postgreWork.get_status_task(taskID)
        if statusTask=='stop':
            break

        messages=postgreWork.get_last_messages_for_user(call.user_id, count=10)   
        allMessages=''
        for message in messages:
            allMessages+=message.text+'\n'
        # pprint(allMessages)     

        messagesList = [
            {"role": "user", "content": allMessages}
        ]

        answerGPT=gpt.answer(system=promt, topic=messagesList)
        
        send_message(call.user_id, answerGPT, taskID)
        time.sleep(random.randint(60, 90))
        # send_message(user['chatID'], 'Задача начата', taskID)
        
    postgreWork.update_status_task(taskID, 'done')
    return 'Task done'

@app.route('/task/stop/<int:taskID>', methods=['POST'])
def stop_task(taskID):
    postgreWork.update_status_task(taskID, 'stop')
    return 'Task stopped'

@app.route('/first-contact/start/<int:taskID>', methods=['POST'])
def first_contact(taskID):
    calls=postgreWork.get_all_calls_for_task(taskID)
    taskStatus=postgreWork.get_status_task(taskID)
    
    if taskStatus=='porocessing':
        return 'Task is already in progress'
    
    postgreWork.get_status_call(taskID, 'processing')
    
    # promt=postgreWork.get_promt_task(taskID)
    firstMessage=postgreWork.get_first_message_task(taskID)
    for call in calls:
        taskStatus=postgreWork.get_status_task(taskID)
        if taskStatus=='stop':
            break
        send_message(call.user_id, firstMessage, taskID)
        postgreWork.update_call_is_first_message(call.id, True)
        # postgreWork.add_call(call., taskID, firstMessage)
        time.sleep(random.randint(60, 90))

    postgreWork.get_status_task(taskID, 'done')
    pass

@app.route('/first-contact/stop/<int:taskID>', methods=['POST'])
def stop_first_contact(taskID):
    postgreWork.update_status_task(taskID, 'stop')
    return 'Call stopped'

@app.route('/create-call/<int:taskID>', methods=['POST'])
def create_call(taskID):
    users=postgreWork.get_all_users_for_task(taskID)
    for user in users:
        postgreWork.add_call(user_id=user.id, groupID=taskID) 
    
    return 'OK'

@app.route('/webhook', methods=['POST'])
def webhook():
    pass    

if __name__ == '__main__':
    pass
    # send_message(2118909508, 'Cамо сообщение', 33 )
    app.run(host='0.0.0.0', port='5002', debug=False) #
