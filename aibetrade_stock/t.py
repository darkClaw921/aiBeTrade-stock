import requests
import json

api_token = '6768830134:AAG1AUgQapY_whU3-VG63n9juJVC5kt7Gp8'
chat_id = '515386623'

api_url = f'https://api.telegram.org/bot{api_token}/getChat?chat_id={chat_id}'

response = requests.get(api_url)
data = response.json()

if data['ok']:
    nickname = data['result']['username']
    print('User nickname:', nickname)
else:
    print('Error:', data['description'])
