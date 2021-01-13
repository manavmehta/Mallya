import random
from config import TOKEN, BASE_TELEGRAM_URL
import helpers as _
import threading
import time
from collections import OrderedDict

updateid_dict = OrderedDict()

def index():
    '''
        Main function that is responsible to run the server.
    '''

    global updateid_dict

    updateCount = _.getLastUpdate(BASE_TELEGRAM_URL)['update_id']
    
    # Keep Listening to incoming requests
    while True:
        update = _.getLastUpdate(BASE_TELEGRAM_URL)
        if update['update_id'] not in updateid_dict.keys():
            updateid_dict[update['update_id']] = time.time()
            print(update,'\n')
            try:
                new_thread = threading.Thread(target = _.parseIncomingMessage, args=(update,))
                new_thread.start()
            except:
                print("Unable to create a thread")

            if len(updateid_dict.keys()) > 50:
                updateid_dict.pop(list(updateid_dict.keys())[0])


if __name__ == '__main__':
    index()
