import random
from config import TOKEN, BASE_TELEGRAM_URL
import helpers as _

def index():
    '''
        Main function that is responsible to run the server.
    '''

    updateCount = _.getLastUpdate(BASE_TELEGRAM_URL)['update_id']
    
    # Keep Listening to incoming requests
    while True:
        update = _.getLastUpdate(BASE_TELEGRAM_URL)
        if updateCount == update['update_id']:
            _.parseIncomingMessage(update)
            updateCount += 1

if __name__ == '__main__':
    index()
