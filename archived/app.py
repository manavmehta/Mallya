#!/usr/bin/env python3

import random
import telebot
from config import TOKEN, BASE_TELEGRAM_URL
import helpers as _
import threading
import time
from collections import OrderedDict

bot = telebot.TeleBot(TOKEN)

updateid_dict = OrderedDict()

def index():
    '''
        Main function that is responsible to run the server.
    '''

    global updateid_dict

    # updateCount = _.getLastUpdate(BASE_TELEGRAM_URL)['update_id'] # variable from stale algo. Should be deleted before release 2.
    
    last_update_id=None

    # Keep Listening to incoming requests
    while True:
        # The following conditional ensures fetching of latest 50 updates
        updates_list = None
        if last_update_id==None:
            updates_list = bot.get_updates()
        else:
            updates_list = bot.get_updates(last_update_id, 100, 20)
        
        for update in updates_list:
 
            last_update_id=update.update_id
        
            if update.update_id not in updateid_dict.keys():
                updateid_dict[update.update_id] = time.time()
                # print(update,'\n')
                try:
                    new_thread = threading.Thread(target = _.parseIncomingMessage, args=(update,))
                    new_thread.start()
                except:
                    print("Unable to create a thread")

                if len(updateid_dict.keys()) > 50:
                    updateid_dict.pop(list(updateid_dict.keys())[0])


if __name__ == '__main__':
    index()

