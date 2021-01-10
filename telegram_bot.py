'''
This file is a no-op. It only refers to as how modular the code of our bot should be.
'''

import requests

from config import TELEGRAM_SEND_MESSAGE_URL

class TelegramBot:

    def __init__(self):
        """"
        Initializes an instance of the TelegramBot class.
        Attributes:
            chat_id:str: Chat ID of Telegram chat, used to identify which conversation outgoing messages should be send to.
            text:str: Text of Telegram chat
            user_name:str: First name of the user who sent the message
        """

        self.chat_id = None
        self.text = None
        self.user_name = None


    def parseWebhookData(self, data):
        """
        Parses Telegram JSON request from webhook and sets fields for conditional actions
        Args:
            data:str: JSON string of data
        """

        message = data['message']

        self.chat_id = message['chat']['id']
        self.incoming_message_text = message['text'].lower()
        self.user_name = message['from']['user_name']


    def action(self):
        """
        Conditional actions based on set webhook data.
        Returns:
            bool: True if the action was completed successfully else false
        """

        success = None

        if self.incoming_message_text == '/hello':
            self.outgoing_message_text = "Hello {}!".format(self.user_name)
            success = self.sendMessage()
        
        if self.incoming_message_text == '/rad':
            self.outgoing_message_text = '🤙'
            success = self.sendMessage()
        
        return success


    def sendMessage(self):
        """
        Sends message to Telegram servers.
        """

        res = requests.get(TELEGRAM_SEND_MESSAGE_URL.format(self.chat_id, self.outgoing_message_text))

        return True if res.status_code == 200 else False
    

    @staticmethod
    def initWebhook(url):
        """
        Initializes the webhook
        Args:
            url:str: Provides the telegram server with a endpoint for webhook data
        """

        requests.get(url)