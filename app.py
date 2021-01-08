import requests as requests
import random
from db import db
from config import TOKEN, BASE_TELEGRAM_URL

def getChatID(update):
    return update['message']['chat']['id']

def getMessageText(update):
    return update['message']['text']

# create function that get getLastUpdate
def getLastUpdate(req):
    response = requests.get(req + 'getUpdates').json()
    result = response['result']
    return result[-1]  # get last record message update

def send_message(chat_id, message_text):
    params = {'chat_id': chat_id, 'text': message_text}
    response = requests.post(BASE_TELEGRAM_URL + 'sendMessage', data=params)
    return response

def prepareReply(db:dict, incoming_message:str, update):
    if incoming_message in ['hi', 'hello']:
        return db[incoming_message].format(update['message']['from']['first_name'])
    else:
        return db[incoming_message].format('')

def index():
    updateCount = getLastUpdate(BASE_TELEGRAM_URL)['update_id']
    # Keep Listening to incoming requests
    while True:
        update = getLastUpdate(BASE_TELEGRAM_URL)
        if updateCount == update['update_id']:
            incoming_message = getMessageText(update).lower()
            if incoming_message in db:
                send_message(getChatID(update), prepareReply(db, incoming_message, update))
            else:
                send_message(getChatID(update), 'Hindi bol bsdk')
            updateCount += 1

if __name__ == '__main__':
    index()
