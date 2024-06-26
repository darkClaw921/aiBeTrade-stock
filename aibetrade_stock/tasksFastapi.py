from fastapi import FastAPI, HTTPException
from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChat, InputPeerUser, PeerUser
from dotenv import load_dotenv
import os
from pprint import pprint
import postgreWork
from chat import GPT
# from workFlask import send_message
import random
import time
import asyncio

load_dotenv()
# Замените значения ниже на ваши
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

gpt = GPT()
app = FastAPI()
client = TelegramClient('session_name_i_own_zergo3', API_ID, API_HASH, system_version="4.16.32-vxCUSTOM", device_model='FastAPI Galaxy S24 Ultra, running Android 14')

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

async def send_message(chatID, message, threadID=None):
    await client.start()
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
        # if chatID == 327475194: return  0
        # try:
        #     from_ = await client.get_entity(chatID)
        # except:
        #     await client.get_dialogs()
        #     from_ = await client.get_entity(chatID)
        user=postgreWork.get_user(chatID)
        print(user.nickname) 
        try:
            await client.send_message(entity=chatID, message=chunk)#work
            return 1
        except:
            await client.get_dialogs()    
        try:
            await client.get_participants(user.nickname)
        except:
            1+0

            # pprint(user.nickname)
                    # await client.get_participants(thread.name)
                # await client.get_participants(threadID)
        try:
            # print(user.nickname) 
            await client.send_message(entity=chatID, message=chunk)#wor
            return 1
        except:
            return None


@app.post('/task/start/{taskID}')
async def start_task(taskID: int):
    # 1/0
    calls = postgreWork.get_all_calls_for_task(taskID)
    statusTask = postgreWork.get_status_task(taskID)
    
    if statusTask == 'processing':
        return 'Task is already in progress'
    
    postgreWork.update_status_task(taskID, 'processing')
    promt = postgreWork.get_promt_task(taskID)
    # print(promt)
    for call in calls:
        if call.is_first_message:
            continue
        statusTask = postgreWork.get_status_task(taskID)
        if statusTask == 'stop':
            break

        messages = postgreWork.get_last_messages_for_user(call.user_id, count=10)
        allMessages = ''.join(message.text + '\n' for message in messages)
        
        messagesList = [{"role": "user", "content": allMessages}]
        answerGPT = gpt.answer(system=promt, topic=messagesList)
        
        # time.sleep(random.randint(60, 90))
        await send_message(call.user_id, answerGPT)
        
        
    postgreWork.update_status_task(taskID, 'done')
    return {'detail': 'Task done'}

@app.post('/task/stop/{taskID}')
async def stop_task(taskID: int):
    postgreWork.update_status_task(taskID, 'stop')
    return {'detail': 'Task stopped'}

@app.post('/first-contact/start/{taskID}')
async def first_contact(taskID: int):
    # 1/0
    calls = postgreWork.get_all_calls_for_task(taskID)
    taskStatus = postgreWork.get_status_task(taskID)
    # print(taskStatus)
    # pprint(calls)
    if taskStatus == 'processing':
        pass
        # return 'Task is already in progress'
    
    postgreWork.update_status_task(taskID, 'processing')
    
    # promtFurstMessage=gpt.load_prompt('')
    
    firstMessage = postgreWork.get_first_message_task(taskID)
    # pprint(calls)
    # groups = postgreWork.get_groups_for_task(taskID)
    users=postgreWork.get_all_users_for_task(taskID)
    Task=postgreWork.get_task(taskID)
    groupID=Task.groups[0]
    promtFirstMessage = gpt.load_prompt(Task.first_message) # это url теперь
    for call in calls:
        if call.is_first_message:
            continue
        taskStatus = postgreWork.get_status_task(taskID)
        if taskStatus == 'stop':
            break
        
        messageUser=postgreWork.get_last_messages_for_user(userID=call.user_id,groupID=groupID, count=2)
        mesUser=''
        for message in messageUser:
            mesUser+=message.text+'\n'

        historyList = [
            {'role': 'user', 'content': mesUser},]
        print(f'{call.user_id=}')
        print(f'{mesUser=}')
        # continue
        firstMessage=gpt.answer(promtFirstMessage, historyList, 0, modelVersion='gpt-3.5-turbo-16k')[0]
        postgreWork.add_call_message(groupID, call.user_id, firstMessage, 'first_system')
        mess= await send_message(chatID=call.user_id, message=firstMessage,threadID=users)
        print(f'{"отправлено":_^30}')
        if mess is not None:
            postgreWork.update_call_is_first_message(call.id, True)
        else: continue

        time.sleep(random.randint(15, 60))
    
    postgreWork.update_status_task(taskID, 'done')
    return {'detail': 'First contact done'}

@app.post('/first-contact/stop/{taskID}')
async def stop_first_contact(taskID: int):
    postgreWork.update_status_task(taskID, 'stop')
    return {'detail': 'First contact stopped'}

@app.post('/call/{taskID}')
async def create_call(taskID: int):
    users = postgreWork.get_all_users_for_task(taskID)
    for message in users:
        try:
            # pprint(message.__dict__)
            postgreWork.add_call(userID=message.user_id, groupID=taskID)
        except:
            continue
    
    return {'detail': 'Calls created'}

@app.post('/webhook')
async def webhook():
    return {'detail': 'Webhook endpoint'}

async def main():
    global client
    await client.start()
    # user=PeerUser(400923372)
    
    # await client.send_message(entity=400923372, message='Hello!')
    # await first_contact(2)
    # di=await client.get_dialogs()
    # pprint(di)


    # await create_call(2)
    # await first_contact(2)

    # di= await client.get_participants('IGYAK')
    # GetFullChatRequest = await client(GetFullChatRequest(-4252722092))
    # pprint(GetFullChatRequest) 
    # pprint(di) 

    # from_ = await client.get_entity(6984701819)
    # pprint(from_.__dict__)



if __name__ == '__main__':
    # import asyncio
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5002) 
    # asyncio.run(main())
    # first_contact(2)
    
