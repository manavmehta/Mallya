# -*- coding: utf-8 -*-

import random
import urllib.parse as url
import os
import logging
import tensorflow_hub as hub
import numpy as np
import requests
import dotenv
from commands import commands
import db

logger = logging.getLogger(__name__)

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")
MODULE_URL = os.getenv("MODULE_URL")
BASE_TELEGRAM_URL = os.getenv("BASE_TELEGRAM_URL").format(TOKEN)

small_talk_questions, small_talk_answers = db.get_smalltalk()
collection_questions, collection_answers = db.get_qna_lists()

user_specific_answers = {}

def get_chat_id(update):
    """
    Returns the chatID from the update.
    """
    return update.message.chat.id

def get_last_update(req, offset: int = None):
    """
    Returns the latest update from the getUpdates bot API call.

    Args:
        req (str): The URL to make the API call to.
        offset (int): The offset value to pass in the API call (default is None).

    Returns:
        List[Dict[str, Any]]: A list of the latest updates from the API call.
    """
    updates_url = f"{req}getUpdates"
    if offset is not None:
        updates_url += f"?offset={offset}"
    try:
        response = requests.get(updates_url, timeout=300).json()
        result = response.get("result", [])
        return result[-5:]
    except (requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.RequestException) as exception:
        logger.error("Error fetching updates: %s", exception)
        return []


def get_user_id(update):
    """
    Returns the userID from the update.
    """
    return update.message.from_user.id


def address_query(update):
    """
    This function handles different types of commands entered by the user.

    Args:
        update (telegram.Update): The incoming update object.

    Returns:
        None.
    """
    
    command, message = parse_incoming_message(update)

    if command == "invalid":
        logger.info("Invalid command entered by the user")
        send_message(
            get_chat_id(update),
            "Please use a valid command or type /help to know the commands. valid commands start with a /. Cheers 🍻",
        )
        return

    elif command == "q":
        answer_query(message, update)

    elif command == "n":
        logger.info("User requested next answer")
        user_specific_answers[get_user_id(update)] = give_one_answer(
            get_chat_id(update), user_specific_answers[get_user_id(update)]
        )

        if len(user_specific_answers[get_user_id(update)]) <= 1:
            send_message(
                get_chat_id(update), "No more answers available for this question."
            )

    elif command == "u" or command == "d":
        logger.info("User voted on an answer")
        vote_on_answer(get_chat_id(update), command, update)

    elif command == "smalltalk":
        logger.info("Smalltalk command entered by the user")
        send_message(get_chat_id(update), address_smalltalk(message))

    else:
        first_name = update.message.from_user.first_name
        if update.message:
            first_name = update.message.from_user.first_name
        else:
            first_name = update.edited_message.text.from_user.first_name
        logger.info("Valid command entered by the user")
        send_message(get_chat_id(update), commands[command].format(first_name))

    return


def parse_incoming_message(update):
    """
    Returns the chatID from the update.
    """

    incoming_message = get_message_text(update).lower()
    command, incoming_message_bifurcated = bifurcate_incoming(incoming_message)
    logger.info("Parsed incoming message: command='%s', message='%s'", command, incoming_message)
    return command, incoming_message_bifurcated


def get_message_text(update):
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


def send_message(chat_id, message_text):
    """
    Sends the <message_text> to the corresponding <chat_id>
    """
    params = {"chat_id": chat_id, "text": message_text}
    try:
        response = requests.post(BASE_TELEGRAM_URL + "sendMessage", timeout=10, data=params)
        logger.info("Message sent successfully to chat ID %s: %s", chat_id, params["text"])
        return response
    except (requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError) as exception:
        logger.exception("Error sending message to chat ID %s: %s", chat_id, exception)


# Bifurcate incoming_message_command into command and incoming message
def bifurcate_incoming(incoming_message_command: str):
    """
    Bifurcates the command and the message into two
    examples:
    /hi -> hi, None
    /q How is IIT Mandi? -> q, How is IIT Mandi
    """
    try:
        command, incoming_message = None, None
        if incoming_message_command[0] != "/":
            return "smalltalk", incoming_message_command
        
        iterator = 1
        command = ""
        while iterator < len(incoming_message_command) and incoming_message_command[iterator] != " ":
            command += incoming_message_command[iterator]
            iterator += 1
        if iterator < len(incoming_message_command):
            incoming_message = incoming_message_command[iterator + 1 :]

        if command not in {"u", "d", "n", "q"} and command not in commands:
            return "invalid", None

        return command, incoming_message
    except Exception as exception:
        logger.exception("Error bifurcating incoming message: %s", exception)
        return "invalid", None

def vote_on_answer(chat_id: int, vote_type: str, update) -> None:
    """
    Registers the user's vote on a specific answer and updates the database accordingly.

    Args:
        chat_id (int): The chat ID where the message is being sent.
        vote_type (str): The type of vote, which can be either "upvote" or "downvote".
        update (Dict[str, Any]): The update object containing the incoming message.

    Returns:
        None
    """
    user_id = get_user_id(update)
    if user_id not in user_specific_answers:
        send_message(chat_id, "Your Vote could not be registered!")
        return
    
    voted_answer = user_specific_answers[user_id][-1]

    user_specific_answers[user_id][-1] = voted_answer
    
    try:
        db.update_vote_qna(vote_type, answer=voted_answer["answer"])
        logger.info("Vote registered successfully.")
        send_message(chat_id, "Your Vote was registered!")
    except Exception as exception:
        logger.exception("Error registering vote: %s", exception)
        send_message(chat_id, "An error occurred while registering your vote. Please try again later.")

def give_one_answer(chat_id: int, answers):
    """
    Sends one answer from the list of <answers> to the corresponding <chat_id>, and cycles the list so that
    the next call to this function returns the next answer. Allows upvoting and downvoting of the answer using
    the commands /u and /d respectively, and getting the next answer using the command /n.

    Args:
        chat_id (int): The ID of the chat to send the message to.
        answers (List[Dict]): The list of answers to choose from.

    Returns:
        List[Dict]: The updated list of answers.

    """
    if not answers:
        raise ValueError("The list of answers is empty.")

    selected_answer = answers[0]
    for i in range(len(answers) - 1):
        answers[i] = answers[i + 1]
    answers[-1] = selected_answer

    message = f"{selected_answer['answer']}\n\n" \
              "___________________________________\n" \
              f"Upvotes: {selected_answer['upvotes']}, Downvotes: {selected_answer['downvotes']}\n\n" \
              "/u to upvote, /d to downvote, or /n for next answer."

    send_message(chat_id, message)

    return answers


def answer_query(incoming_message: str, update) -> None:
    """
    Answer a user's query by finding relevant answers and displaying them.
    
    Args:
        incoming_message (str): The user's query.
        update (Telegram update): The Telegram update object.
    """
    try:
        features = model([incoming_message] + collection_questions)
        answers = find_answers(features)
        logger.info("Received answers for query: %s", incoming_message)
        if len(answers) == 0:
            message = "This question hasn't yet been answered. I will ask maintainers to answer it.\nTry a Google search till then:\n"
            search_url = f"https://www.google.com/search?q={url.quote(incoming_message)}"
            send_message(get_chat_id(update), message + search_url)
        else:
            answers = give_one_answer(get_chat_id(update), answers)
        user_specific_answers[get_user_id(update)] = answers
    except Exception as exception:
        logger.exception("Error while answering query: %s", exception)
        error_msg = "Oops! Something went wrong while answering your query. Please try again later."
        send_message(get_chat_id(update), error_msg)

def address_smalltalk(question: str) -> str:
    """
    Generates a small talk response based on the given question.

    Args:
        question (str): The user's question.

    Returns:
        str: The generated small talk response.
    """
    try:
        features = model([question] + small_talk_questions)

        corr = np.inner(features, features)

        if max(corr[0][1:]) < 0.4 or corr[0][1:].argmax() >= len(small_talk_answers):
            return "I didn't understand that :("
        
        return random.choice(small_talk_answers[corr[0][1:].argmax()].split("&&"))
    except Exception as exception:
        logger.exception("Error while generating small talk response: %s", exception)
        return "Oops! Something went wrong while generating a response. Please try again later."

def find_answers(features):
    """
    Find answers from the database for a given set of features.
    
    Args:
        features (List[float]): The features of the user's question.
        
    Returns:
        List[Dict[str, Union[str, int]]]: The list of matching answers from the database.
    """
    try:
        corr = np.inner(features, features)

        if max(corr[0][1:]) > 0.4:
            relevant_question_index = corr[0][1:].argmax()

            if relevant_question_index >= len(collection_questions):
                return []

            relevant_question = collection_questions[relevant_question_index]
            logger.info("Matching question found in database: %s", relevant_question)
            answers = db.find_in_qna(relevant_question)
            return answers

        return []
    except Exception as exception:
        logger.exception("Error while finding answers for query: %s", exception)
        return []


logger.info("Loading NLP Model, it might take a few minutes for the first time")
model = hub.load(MODULE_URL)
logger.info("NLP model loaded successfully")
