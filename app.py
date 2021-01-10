import random
from config import TOKEN, BASE_TELEGRAM_URL
import helpers as _
import gspread
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

def index():
    '''
        Main function that is responsible to run the server.
    '''

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

    updateCount = _.getLastUpdate(BASE_TELEGRAM_URL)['update_id']

    print("\nListening to Questions now !\n")
    # Keep Listening to incoming requests
    while True:

        if (updateCount + 1) / 100 != updateCount / 100:                #fetching updates(if any) in sheet
            questions = [w.lower() for w in worksht.col_values(1)[1:]]
            answers = worksht.col_values(2)[1:]

        update = _.getLastUpdate(BASE_TELEGRAM_URL)
        if updateCount == update['update_id']:
            
            incoming_message = _.getMessageText(update).lower()
            msg_embeddings = model([incoming_message] + questions)
            

            _.send_message(_.getChatID(update), _.find_answer([incoming_message] + questions, msg_embeddings, answers))
            
            # if incoming_message in db:
            #     send_message(getChatID(update), prepareReply(db, incoming_message, update))
            # else:
            #     send_message(getChatID(update), 'Hindi bol bsdk')
            updateCount += 1

if __name__ == '__main__':
    index()
