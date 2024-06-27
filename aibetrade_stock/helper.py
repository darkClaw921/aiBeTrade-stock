from datetime import datetime, timedelta
# import workYDB
# from workYDB import *
import redis
import json
from chat import GPT
from dotenv import load_dotenv
import os
from pprint import pprint
import time
import requests
from workBinance import get_BTC_analit_for, get_price_now
# from loguru import logger
import random 
from workFlask import send_message
from postgreWork import *
import aiohttp
load_dotenv()
# sql = workYDB.Ydb()

gpt = GPT()

# GPT.set_key(os.getenv('KEY_AI'))

STOCK_URL = os.environ.get('STOCK_URL')

coins = {'Bitcoin':'BTCUSDT', 
    'Ethereum':'ETHUSDT',
    'Bnb':'BNBUSDT',
    'Ripple':'XRPUSDT',
    'Cardano':'ADAUSDT',
    'Dogecoin':'DOGEUSDT',
    'Solana':'SOLUSDT',
    'Tron':'TRXUSDT',
    'Polkadot':'DOTUSDT',
    'Polygon':'MATICUSDT'}

coins2 =[ 
    {'name': 'Bitcoin', 'code': 'BTCUSDT'},
    {'name': 'Ethereum', 'code': 'ETHUSDT'},
    {'name': 'Bnb', 'code': 'BNBUSDT'},
    {'name': 'Ripple', 'code': 'XRPUSDT'},
    {'name': 'Cardano', 'code': 'ADAUSDT'},
    {'name': 'Dogecoin', 'code': 'DOGEUSDT'},
    {'name': 'Solana', 'code': 'SOLUSDT'},
    {'name': 'Tron', 'code': 'TRXUSDT'},
    {'name': 'Polkadot', 'code': 'DOTUSDT'},
    {'name': 'Polygon', 'code': 'MATICUSDT'}]
#datetime
def time_epoch():
    from time import mktime
    dt = datetime.now()
    sec_since_epoch = mktime(dt.timetuple()) + dt.microsecond/1000000.0

    millis_since_epoch = sec_since_epoch * 1000
    return int(millis_since_epoch)

def get_dates_YDB(day):
    # Текущая дата
    #patern = '2023-07-18T20:26:32'
    patern = '%Y-%m-%dT%H:%M:%SZ'
    current_date = datetime.now().strftime(patern)

    # Дата, отстоящая на 30 дней
    delta = timedelta(days=day)
    future_date = (datetime.now() + delta).strftime(patern)

    return current_date, future_date

def get_dates(day, pattern = '%d/%m/%Y'):
    # Текущая дата
    current_date = datetime.now().strftime(pattern)

    # Дата, отстоящая на 30 дней
    delta = timedelta(days=day)
    future_date = (datetime.now() + delta).strftime(pattern)

    return current_date, future_date

def timestamp_to_date(timestap, pattern='%Y-%m-%dT%H:%M:%SZ'):
   
    """timestamp

    Returns:
        str: %Y-%m-%dT%H:%M:%SZ
    """
    a = time.gmtime(timestap)
    date_time = datetime(*a[:6])
    date_string = date_time.strftime(pattern)
    
    return date_string

def date_now():
    #patern = '%Y-%m-%dT%H:%M:%S'
    patern = '%Y-%m-%dT%H:00:00'
    #patern = '%Y-%m-%dT%H'
    current_date = datetime.now().strftime(patern)
    return current_date+'Z'
#YDB
def prepare_prognoz(text):
    import re
    # print(text)
    pattern = r"\d+\.\d+"
    matches = re.findall(pattern, text)
    lowerPrice = 0
    upperPrice = 0
    if len(matches)==3:
        prognozPrice = matches[0]
        lowerPrice = matches[1]
        upperPrice = matches[2]
    elif len(matches)==4:
        prognozPrice = matches[0]
        lowerPrice = matches[2]
        upperPrice = matches[3]
    else:
        # logger.debug(f'{matches=}')
        # logger.debug(f'{text=}')
        prognozPrice = matches[0]
    # pprint(matches)
    return prognozPrice, lowerPrice, upperPrice


def forecastText(day:int, coin='Bitcoin'):
    dateNow = date_now()

    #TODO взять последний от этого часа прогноз
    # rows = sql.select_query('prognoz_text',f"date = CAST('{dateNow}' as datetime) and coin = '{coin}'")
    # if rows != []:
    #     text = rows[0]['textPrognoz']
    #     return text
    promtUrl = 'https://docs.google.com/document/d/1_Ft4sDJJpGdBX8k2Et-OBIUtvO0TSuw8ZSjbv5r7H7I/edit?usp=sharing'
    PROMT_URL = promtUrl 
    #promt = gpt.load_prompt(promptUrl)
    try:
        promt = gpt.load_prompt(PROMT_URL)
    except:
        time.sleep(60)
        promt = gpt.load_prompt(PROMT_URL)
    #promt = 
    #print(f'{promptUrl=}')
    
    #print(f'{analitBTC}')
    analitBTC = get_BTC_analit_for(day, coin)
    current, future = get_dates(day)
    priceNow = str(get_price_now(coin)) 

    print("Текущая дата:", current)
    print(f"Дата через {day} дней:", future)
    promt = promt.replace('[analitict]', analitBTC)
    promt = promt.replace('[nextDate]', str(day))
    promt = promt.replace('[coin]', coin)
    promt = promt.replace('[nowDate]', future)
    promt = promt.replace('[exchangerate]', priceNow)

    print('#########################################', promt)
    try:
        mess = [{'role': 'system', 'content': promt,},
                {'role': 'user', 'content': ' '}]
        random_time = random.randint(5, 30)
        #time.sleep(random_time)
        #answer, allToken, allTokenPrice= gpt.answer(' ',mess,)
        
        primt1URL = 'https://docs.google.com/document/d/1kvtS8FDYQ7Mg0QTuIYLUzfzPzIwNtNAy8nVHTDcmH1A/edit?usp=sharing'
        promt = gpt.load_prompt(primt1URL)
        promt = promt.replace('[analitict]', analitBTC)
        promt = promt.replace('[nextDate]', str(day))
        promt = promt.replace('[coin]', coin)
        promt = promt.replace('[nowDate]', future)
        promt = promt.replace('[exchangerate]', priceNow)
        mess = [{'role': 'system', 'content': promt,},
                {'role': 'user', 'content': ' '}]
        answer1, allToken1, allTokenPrice1= gpt.answer(' ',mess,)
        
        random_time = random.randint(5, 30)
        #time.sleep(random_time)
        primt2URL= 'https://docs.google.com/document/d/15nj87WI9Ud3EGgmp0JM0AZdQVQGPgN3ly-zjWCEUsB0/edit?usp=sharing'
        promt = gpt.load_prompt(primt2URL)
        promt = promt.replace('[analitict]', analitBTC)
        promt = promt.replace('[nextDate]', str(day))
        promt = promt.replace('[coin]', coin)
        promt = promt.replace('[nowDate]', future)
        promt = promt.replace('[exchangerate]', priceNow)
        mess = [{'role': 'system', 'content': promt,},
                {'role': 'user', 'content': ' '}]
        answer2, allToken2, allTokenPrice2= gpt.answer(' ',mess,)
        

        primt3URL= 'https://docs.google.com/document/d/17hsm51kQGnhXgU7LkFkCGxsIBY82FPefowN8GcGIa6U/edit?usp=sharing'
        promt = gpt.load_prompt(primt3URL)
        mess = [{'role': 'system', 'content': promt,},
                {'role': 'user', 'content': f"{answer1}\n{answer2}"}]
        answer3, allToken3, allTokenPrice3= gpt.answer(' ',mess,)
        
        random_time = random.randint(5, 30)
        #time.sleep(random_time)
        primt4URL= 'https://docs.google.com/document/d/1cqDETdeSLj2vX8nBzWFbNV4jAl61oz_nGwL16EM-ZIM/edit?usp=sharing'
        promt = gpt.load_prompt(primt4URL)
        promt = promt.replace('[language]', 'Russian')

        mess = [{'role': 'system', 'content': promt,},
                {'role': 'user', 'content': f"{answer1} {answer2} {answer3}"}]
        answer4, allToken4, allTokenPrice4= gpt.answer(' ',mess,)

        answer = answer4
        allToken = allToken1+allToken2+allToken3+allToken4
        allTokenPrice = allTokenPrice1+allTokenPrice2+allTokenPrice3+allTokenPrice4

        promt5URL = 'https://docs.google.com/document/d/1TPTa7s_VsbjMdaHw0k0EQrHecSnp8X5T-JoaOoGh53M/edit?usp=sharing'
        promt = gpt.load_prompt(promt5URL)
        promt = promt.replace('[analitict]', analitBTC)
        promt = promt.replace('[coin]', coin)
        promt = promt.replace('[exchangerate]', priceNow)
        # promt = promt.replace('[language]', 'Russian')

        mess = [{'role': 'system', 'content': promt,},
                {'role': 'user', 'content': f""}]
        #print(promt)
        answer5, allToken5, allTokenPrice5= gpt.answer(' ',mess,) 
        # prognozPrice, lowerPrice, upperPrice = prepare_prognoz(answer5)
        
        allTokenPrice += allTokenPrice5
        allToken += allToken5
        

        # dateForDatePrognoz = get_dates(1,'%Y-%m-%dT%H:00:00')[1]+'Z'
        # dateForDatePrognoz = datetime.now() + timedelta(days=1)
        #price_for_date_prognoz = get_price_now()
        # row = {
        #     'time_epoh':time_epoch(),
        #     'date':dateNow,
        #     'textPrognoz': answer,
        #     'coin':coin,
        #     'stock': 'Binance',
        #     'allToken':allToken,
        #     'allTokenPrice':allTokenPrice,
        #     'textPricePrognoz': answer5,
        #     'lowerPrice':lowerPrice,
        #     'upperPrice':upperPrice,
        #     'pricePrognoz':prognozPrice,
        #     'dateForDatePrognoz':dateForDatePrognoz,
        #     'priceNow':priceNow,
        # }
        # # logger.debug(row=row)
        # # sql.insert_query('prognoz_text', row)
        # # postgreWork.add_new_row_prognoz_text(row)

        # row = {
        #     'time_epoh':time_epoch(), 
        #     'currencyPair':coins[coin],
        #     'priceClose':prognozPrice,
        #     'dateClose':dateForDatePrognoz,
        #     'type': 'prognoz',
        #     'strat':'GPT24',
        # }
        # sql.insert_query('analitic', row)
        # postgreWork.add_new_row_analitic(row)

        # print(answer)
        
        #ббольшой текст
        # send_message(-1002118909508,answer,1)

        # send_message(-1002118909508,answer5,1)
        send_message(-1002247551722,answer5,1)
        # send_message(-1002247551722, message=answer)
        return answer
    except Exception as e:
        print(e.__traceback__)
        pprint(e)
        # logger.debug(f'{e=}')

import re
def abt_serch(command: str):
    # Регулярные выражения для команд
    start_new_task_pattern = r'start_new_task name="(.+?)" link_promt="(.+?)" message="(.+?)"'
    view_task_pattern = r'view_task'
    change_task_pattern = r'change_task id=(\d+) name="(.+?)" link_promt="(.+?)" message="(.+?)"'
    delete_task_pattern = r'delete_task id_task=(\d+)'
    add_new_channel_pattern = r'add_new_channel id_task=(\d+) id_channel=(\d+)'
    view_channel_pattern = r'view_channel id_task=(\d+)'
    change_channel_pattern = r'change_channel id_task=(\d+) id_channel=(\d+)'
    delete_channel_pattern = r'delete_channel id_task=(\d+)'
    start_search_pattern = r'start_search id=(\d+) id_channel=(\d+)'
    stop_search_pattern = r'stop_search id=(\d+)'
    status_task_pattern = r'status_task id=(\d+)'
    count_search_pattern = r'count_search id_task=(\d+)'
    start_call_pattern = r'start_call id_task=(\d+)'
    create_call_pattern =r'create_call id_task=(\d+)'
    # session = Session()
    with Session() as session:
        match command:
            case _ if re.match(start_new_task_pattern, command):
                name, link_prompt, message = re.findall(start_new_task_pattern, command)[0]
                new_task = Task(created_date=datetime.now(), first_message=message, promt_message=link_prompt, status='New')
                session.add(new_task)
                session.commit()
                task_id = new_task.id
                return f'Task new add successful. ID TASK={task_id}'

            case _ if re.match(view_task_pattern, command):
                try:
                    tasks = session.query(Task).all()
                except Exception as e:
                    print(f"An error occurred: {e}")
                    session.rollback()  # Откат транзакции
                    return 'An error occurred while retrieving the list of tasks.'
                
                return [(task.id, task.first_message, task.promt_message, task.status) for task in tasks]

            case _ if re.match(change_task_pattern, command):
                task_id, name, link_prompt, message = re.findall(change_task_pattern, command)[0]
                print(task_id, name, link_prompt, message)
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.first_message = message
                    task.promt_message = link_prompt
                    task.status = name
                    session.commit()
                    return f'Task {task_id} updated successfully.'

            case _ if re.match(delete_task_pattern, command):
                task_id = re.findall(delete_task_pattern, command)[0]
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    session.delete(task)
                    session.commit()
                    return f'Task {task_id} deleted successfully.'

            case _ if re.match(add_new_channel_pattern, command):
                task_id, channel_id = re.findall(add_new_channel_pattern, command)[0]
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.groups.append(int(channel_id))
                    session.commit()
                    return f'Channel {channel_id} added to task {task_id} successfully.'

            case _ if re.match(view_channel_pattern, command):
                task_id = re.findall(view_channel_pattern, command)[0]
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    return task.groups

            case _ if re.match(change_channel_pattern, command):
                task_id, channel_id = re.findall(change_channel_pattern, command)[0]
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.groups = [int(channel_id)]
                    session.commit()
                    return f'Channel {channel_id} for task {task_id} updated successfully.'

            case _ if re.match(delete_channel_pattern, command):
                task_id = re.findall(delete_channel_pattern, command)[0]
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.groups = []
                    # session.commit()
                    return f'Channel for task {task_id} deleted successfully.'

            case _ if re.match(start_search_pattern, command):
                task_id, channel_id = re.findall(start_search_pattern, command)[0]
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.status = 'Search'
                    session.commit()
                    # Отправка сообщения в телеграм о статусе
                    return f'Status: Search completed  ID Task: {task_id}'

            case _ if re.match(stop_search_pattern, command):
                task_id = re.findall(stop_search_pattern, command)[0]
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.status = 'Stop'
                    session.commit()
                    # Отправка сообщения в телеграм о статусе
                    return f'Status: Stop completed  ID Task: {task_id}'

            case _ if re.match(status_task_pattern, command):
                task_id = re.findall(status_task_pattern, command)[0]
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    return (task.id, task.first_message, task.promt_message, task.status)

            case _ if re.match(count_search_pattern, command):
                task_id = re.findall(count_search_pattern, command)[0]
                count = session.query(Calls).filter(Calls.task_id == task_id).distinct(Calls.user_id).count()
                return f'Unique users for task {task_id}: {count}'
            
            case _ if re.match(start_call_pattern, command):
                task_id = re.findall(start_call_pattern, command)[0]
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.status = 'Calling'
                    session.commit()
                    # a = await aiohttp.request('POST', f'http://159.223.5.4:5002/first-contact/start/{task_id}')
                    requests.post(f'http://159.223.5.4:5002/first-contact/start/{task_id}',timeout=1)
                    # Отправка сообщения в телеграм о статусе
                    return f'Status: Calling completed  ID Task: {task_id}'
            
            case _ if re.match(create_call_pattern, command):
                task_id = re.findall(create_call_pattern, command)[0]
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    # task.status = 'Calling'
                    #создать звоноки
                    # await aiohttp.request('POST', f'http://159.223.5.4:5002/call/{task_id}')
                    requests.post(f'http://159.223.5.4:5002/call/{task_id}',timeout=1)
                    # session.commit()
                    # Отправка сообщения в телеграм о статусе
                    return f'Status: Calling create completed  ID Task: {task_id}'

            case _:
                return 'Invalid command.'



if __name__ == '__main__':

    # send_message(-1002118909508,'test',1)
    taskSTR='change_task id=1 name="test2" link_promt="https://t.me" message="Текст первого приветственного сообщения"'
    # taskSTR='view_task'
    a = abt_serch(taskSTR)
    pprint(a) 
    a=forecastText(0) 
    print(a)
    # send_message(2118909508,a,1)
    # print(a)
    
   