#!/usr/bin/env python3
"""
primary entry point to the bot backend
"""

import os
import time
import signal
import logging
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
import dotenv
import telebot
from telebot.types import Update
import utils

# Load environment variables
dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# Initialize update ID dictionary and logger
updateid_dict = OrderedDict()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define maximum threads and updates to fetch
MAX_THREADS = 10
MAX_UPDATES = 100

# Initialize the thread pool
executor = ThreadPoolExecutor(max_workers=MAX_THREADS)


def fetch_updates(offset):
    """
    Fetch updates from the Telegram server.
    """
    return (
        bot.get_updates()
        if offset is None
        else bot.get_updates(offset, MAX_UPDATES, timeout=20)
    )


def process_update(update: Update):
    """
    Process an incoming update.
    """
    if update.update_id not in updateid_dict:
        updateid_dict[update.update_id] = time.time()
        try:
            executor.submit(utils.address_query, update)
        except Exception as exception:
            logging.error(
                "Unable to process update {%s}: {%s}", update.update_id, exception
            )

        if len(updateid_dict) > 50:
            updateid_dict.popitem(last=False)


def run_bot():
    """
    Main function that runs the bot.
    """
    logging.info("Bot is starting...")
    last_update_id = None

    while True:
        try:
            updates_list = fetch_updates(last_update_id)
            for update in updates_list:
                last_update_id = update.update_id
                process_update(update)
        except Exception as e:
            logging.error("Error while fetching or processing updates: {%s}", e)
            time.sleep(5)  # Sleep for a bit before retrying


if __name__ == "__main__":
    run_bot()
