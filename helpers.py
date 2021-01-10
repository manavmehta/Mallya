import requests as requests
from config import TOKEN, BASE_TELEGRAM_URL
from commands import commands

def getChatID(update):
    '''
        Returns the chatID from the update.
    '''
    return update['message']['chat']['id']

def getMessageText(update):
    '''
        Returns the actual text(payload) from the message/edited_message.
        These two are types of updates sent by teegram API.
        message is just a simple message sent by the user.
        edited_message is when the previous message was edited.
    '''
    if ('message' in update.keys()):
        return update['message']['text']
    else:
        return update['edited_message']['text']

# create function that get getLastUpdate
def getLastUpdate(req):
    '''
        Returns the latest update from the getUpdates bot API call.
    '''
    response = requests.get(req + 'getUpdates').json()
    result = response['result']
    return result[-1]  # get last record message update

def send_message(chat_id, message_text):
    '''
        Sends the <message_text> to the corresponding <chat_id>
    '''
    params = {'chat_id': chat_id, 'text': message_text}
    response = requests.post(BASE_TELEGRAM_URL + 'sendMessage', data=params)
    return response


# Bifurcate incoming_message_command into command and incoming message
def bifurcate(incoming_message_command):
    '''
        Bifurcates the command and the message into two
        examples:
        /hi -> hi, None
        /q How is IIT Mandi? -> q, How is IIT Mandi
    '''
    command, incoming_message = None, None
    if (incoming_message_command[0]!='/'): # Any message that does not start with a / is not a valid command
        return 'invalid', None
    else:
        i=1
        command = ''
        while (i<len(incoming_message_command) and incoming_message_command[i]!=' '):
            command+=incoming_message_command[i]
            i+=1
        if(i<len(incoming_message_command)):
            incoming_message = incoming_message_command[i+1:]

    return command, incoming_message

def replyToCommand(chatID, command, first_name):
    '''
        This is called when the message is any valid command except for a query.
        ie. For all commands available in commands.py
    '''
    send_message(chatID, commands[command].format(first_name))
    return


def answerQuery(commands:dict, incoming_message:str, update):
    
    if incoming_message in ['hi', 'hello']:
        return commands[incoming_message].format(update['message']['from']['first_name'])
    else:
        return commands[incoming_message].format('')

def parseIncomingMessage(update):
    '''
        Returns the chatID from the update.
    '''
    incoming_message_command = getMessageText(update).lower()
    print(type(incoming_message_command))
    command, incoming_message = bifurcate(incoming_message_command)
    print('command = ', command, '\nincoming message = ', incoming_message)
    if (command=='invalid'):
        send_message(getChatID(update), 'Please use a valid command or type /help to know the commands I know. All valid commands start with a slash /. Cheers 🍻')
        return
    elif (command=='q'):
        print(incoming_message)
        # All the code to answering the query goes here.
        # if incoming_message in commands:
        #     send_message(getChatID(update), answerQuery(commands, incoming_message, update))
        # else:
        #     send_message(getChatID(update), 'Hindi bol bsdk')
    else:
        first_name = update['message']['from']['first_name']
        if ('message' in update.keys()):
            first_name = update['message']['from']['first_name']
        else:
            first_name = update['edited_message']['text']['from']['first_name']
        replyToCommand(getChatID(update), command, first_name)

    return
