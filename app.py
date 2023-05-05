#!/usr/bin/env python3

import threading
import time
from collections import OrderedDict
import os
import telebot
import dotenv
import utils

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

updateid_dict = OrderedDict()


def index():
    """
    Main function that is responsible to run the server.
    """

    last_update_id = None

    # Keep Listening to incoming requests
    while True:
        # The following conditional ensures fetching of latest 50 updates
        updates_list = None
        if last_update_id is None:
            updates_list = bot.get_updates()
        else:
            updates_list = bot.get_updates(last_update_id, 100, 20)

        for update in updates_list:
            last_update_id = update.update_id

            if update.update_id not in updateid_dict.keys():
                updateid_dict[update.update_id] = time.time()
                try:
                    new_thread = threading.Thread(
                        target=utils.address_query, args=(update,)
                    )
                    new_thread.start()
                except Exception as exception:
                    print("Unable to create a thread")
                    raise exception

                if len(updateid_dict.keys()) > 50:
                    updateid_dict.pop(list(updateid_dict.keys())[0])


if __name__ == "__main__":
    index()
