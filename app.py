import requests as requests
import random
from db import db
from config import TOKEN, BASE_TELEGRAM_URL
import gspread
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

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

def find_answer(questions, features, answers):       # check database questions for similarity and return suitable answer.
    corr = np.inner(features, features)
    
    if max(corr[0][1:]) < 0.3:
        return "This question hasn't yet been answered."
    else:
        idx = corr[0][1:].argmax()
        return questions[1:][idx]                   # change this to answers[idx] once answers have been uploaded to sheets.

def index():

    gc = gspread.service_account()

    print ('\nLoading NLP Model...\n')
    module_url = "https://tfhub.dev/google/universal-sentence-encoder/4" #@param ["https://tfhub.dev/google/universal-sentence-encoder/4", "https://tfhub.dev/google/universal-sentence-encoder-large/5"]
    model = hub.load(module_url)
    print ('\nNLP model loaded successfully !\n')

    print('\nFetching Questions...\n')
    sht = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Jged2Bis3KymVCfBqdaSUf6mJZm0iJDWai3QxtrkLHQ/edit#gid=0')
    worksht = sht.get_worksheet(0)
    questions = [w.lower() for w in worksht.col_values(1)[1:]]
    answers = worksht.col_values(2)[1:]
    print('\nQuestions fetched succesfully !\n')

    updateCount = getLastUpdate(BASE_TELEGRAM_URL)['update_id']

    print("\nListening to Questions now !\n")
    # Keep Listening to incoming requests
    while True:

        if (updateCount + 1) / 100 != updateCount / 100:                #fetching updates(if any) in sheet
            questions = [w.lower() for w in worksht.col_values(1)[1:]]
            answers = worksht.col_values(2)[1:]

        update = getLastUpdate(BASE_TELEGRAM_URL)
        if updateCount == update['update_id']:
            
            incoming_message = getMessageText(update).lower()
            msg_embeddings = model([incoming_message] + questions)
            

            send_message(getChatID(update), find_answer([incoming_message] + questions, msg_embeddings, answers))
            
            # if incoming_message in db:
            #     send_message(getChatID(update), prepareReply(db, incoming_message, update))
            # else:
            #     send_message(getChatID(update), 'Hindi bol bsdk')
            updateCount += 1

if __name__ == '__main__':
    index()
