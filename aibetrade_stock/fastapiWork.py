from fastapi import FastAPI, HTTPException,Form,Depends
import requests
from pprint import pprint
import os
from dotenv import load_dotenv
# from fastapi.security import OAuth2PasswordBearer
load_dotenv()

from typing import Annotated

# from fastapi import FastAPI, 
TOKEN_BOT = os.getenv('TOKEN_BOT_EVENT')
app = FastAPI(debug=False)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}


# TOKEN_BOT = "YOUR_TELEGRAM_BOT_TOKEN"  # Замените на токен вашего бота
# bot = Bot(token=TOKEN,)
@app.get("/check_user_in_chat/")
async def check_user_in_chat(user_id: int, chat_id: int):
    
    url = f'https://api.telegram.org/bot{TOKEN_BOT}/getChatMember'
    params = {
        'chat_id': f'-100{chat_id}',
        'user_id': user_id
    }
    response = requests.get(url, params=params)
    data = response.json()
    pprint(params)
    pprint(data)
    
    if data['ok']:
        status = data['result']['status']
        if status in ['member', 'administrator', 'creator']:
            return {"in_chat": True}
        else:
            return {"in_chat": False}
    else:
        return {"in_chat": False}
        # raise HTTPException(status_code=400, detail="Error fetching chat member information")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
