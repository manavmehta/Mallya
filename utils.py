# -*- coding: utf-8 -*-

import random
import urllib.parse as url
import os
from pprint import pprint
from commands import commands
import db
import tensorflow_hub as hub
import numpy as np
import requests
import dotenv
from config import BASE_TELEGRAM_URL

dotenv.load_dotenv()
MODULE_URL = os.getenv("MODULE_URL")

small_talk_questions, small_talk_answers = db.get_smalltalk()
collection_questions, collection_answers = db.get_qna_lists()

user_specific_answers = {}

def getChatID(update):
    """
    Returns the chatID from the update.
    """
    return update.message.chat.id



# create function that get getLastUpdate
def getLastUpdate(req, offset=None):
    """
    Returns the latest update from the getUpdates bot API call.
    """
    updates_url = req + "getUpdates"
    if offset != None:
        updates_url += "?offset={}".format(offset)
    response = requests.get(updates_url, timeout=300
                            ).json()
    result = response["result"]
    return result[-5:]  # get last record message update


def getUserID(update):
    """
    Returns the userID from the update.
    """
    return update.message.from_user.id


def addressQuery(update):
    

    if getUserID(update) not in user_specific_answers:
        sendMessage(
            getChatID(update),
            "Please use a valid command or type /help to know the commands I know. All valid commands start with a slash /. Cheers 🍻",
        )

    command, message = parseIncomingMessage(update)

    if command == "invalid":
        sendMessage(
            getChatID(update),
            "Please use a valid command or type /help to know the commands. valid commands start with a /. Cheers 🍻",)
        return

    elif command == "q":
        answerQuery(message, update)

    elif command == "n":
        """
        n = next answer (for the same question)
        """
        user_specific_answers[getUserID(update)] = giveOneAnswer(
            getChatID(update), user_specific_answers[getUserID(update)]
        )

        if len(user_specific_answers[getUserID(update)]) <= 1:
            sendMessage(
                getChatID(update), "No more answers available for this question."
            )

    elif command == "u" or command == "d":
        """
        u = upvote current answer
        d =  downvote current answer
        """
        voteOnAnswer(getChatID(update), command, update)
        
    elif command == "smalltalk":
        sendMessage(getChatID(update), addressSmalltalk(message))

    else:
        first_name = update.message.from_user.first_name
        if update.message:
            first_name = update.message.from_user.first_name
        else:
            first_name = update.edited_message.text.from_user.first_name
        sendMessage(getChatID(update), commands[command].format(first_name))

    return


def parseIncomingMessage(update):
    """
    Returns the chatID from the update.
    """

    incoming_message = getMessageText(update).lower()
    command, incoming_message_bifurcated = bifurcate_incoming(incoming_message)
    pprint({"command": command, "incoming message": incoming_message})
    return command, incoming_message_bifurcated


def getMessageText(update):
    """
    Returns the actual text(payload) from the message/edited_message.
    These two are types of updates sent by teegram API.
    message is just a simple message sent by the user.
    edited_message is when the previous message was edited.
    """
    if update.message:
        return update.message.text
    else:
        return update.edited_message.text



def sendMessage(chat_id, message_text):
    """
    Sends the <message_text> to the corresponding <chat_id>
    """
    params = {"chat_id": chat_id, "text": message_text}
    response = requests.post(BASE_TELEGRAM_URL + "sendMessage", timeout=10, data=params)
    return response


# Bifurcate incoming_message_command into command and incoming message
def bifurcate_incoming(incoming_message_command):
    """
    Bifurcates the command and the message into two
    examples:
    /hi -> hi, None
    /q How is IIT Mandi? -> q, How is IIT Mandi
    """
    command, incoming_message = None, None
    if (
        incoming_message_command[0] != "/"
    ):  # Any message that does not start with a / is not a valid command
        return "smalltalk", incoming_message_command  # decision tree
    else:
        i = 1
        command = ""
        while i < len(incoming_message_command) and incoming_message_command[i] != " ":
            command += incoming_message_command[i]
            i += 1
        if i < len(incoming_message_command):
            incoming_message = incoming_message_command[i + 1 :]

    if command in {"u", "d", "n", "q"} or command in commands:
        return command, incoming_message
    else:
        return "invalid", None

def voteOnAnswer(chatID, vote_type, update):
    if getUserID(update) not in user_specific_answers:
        sendMessage(chatID, "Your Vote could not be registered!")
        return
    
    voted_answer = user_specific_answers[getUserID(update)][-1]
    pprint(voted_answer)

    user_specific_answers[getUserID(update)][-1] = voted_answer
    
    db.update_vote_qna(vote_type, answer=voted_answer["answer"])
    sendMessage(chatID, "Your Vote was registered!")


def giveOneAnswer(chatID, answers):

    # swap first and last element of the array to cycle through the answers.
    selected_answer = answers[0]
    for i in range(0, len(answers) - 1):
        answers[i] = answers[i + 1]
    answers[-1] = selected_answer

    message = selected_answer["answer"] + "\n\n" + "___________________________________\n"
    message += (
        "\nUpvotes: {}, Downvotes: {}".format(selected_answer["upvotes"], selected_answer["upvotes"])
        + "\n\n"
        + "Type /u or /d for upvoting or downvoting this answer or /n for next answer."
    )

    sendMessage(chatID, message)

    return answers


def answerQuery(incoming_message, update):
    features = model([incoming_message] + collection_questions)
    answers = findAnswers(features)
    pprint({"answers_received": answers})

    if len(answers) == 0:
        message = "This Question hasn't yet been answered. I will ask maintainers to answer it.\nTry a Google search till then:\n"
        search_url = "https://www.google.com/search?q={}".format(
            url.quote(incoming_message)
        )
        sendMessage(getChatID(update), message + search_url)
    else:
        answers = giveOneAnswer(getChatID(update), answers)

    user_specific_answers[
        getUserID(update)
    ] = answers


def addressSmalltalk(ques):
    features = model([ques] + small_talk_questions)

    corr = np.inner(features, features)

    if max(corr[0][1:]) < 0.4 or corr[0][1:].argmax() >= len(small_talk_answers):
        return "I didn't understand that :("
    print(small_talk_answers[corr[0][1:].argmax()])
    return random.choice(small_talk_answers[corr[0][1:].argmax()].split("&&"))


def findAnswers(features):                  # check database questions for similarity and return suitable answer.
    
    global collection_answers

    corr = np.inner(features, features)
    
    if max(corr[0][1:]) > 0.4:
        relevant_question_index = corr[0][1:].argmax()

        if relevant_question_index >= len(collection_questions):
            return []
        
        relevant_question = collection_questions[relevant_question_index]
        pprint({"releveant_question": relevant_question})
        answers = db.find_in_qna(relevant_question)
        return answers
    
    return []


pprint("Loading NLP Model, it might take a few minutes for the first time")
model = hub.load(MODULE_URL)
pprint("\nNLP model loaded successfully\n")