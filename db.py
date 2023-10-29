"""
program to setup db
"""

import os
import logging
import dotenv
from pymongo import MongoClient


logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv()
DB_URL = os.getenv("MALLYA_DB_URL")
DB_NAME = "MallyaDB"

logger = logging.getLogger(__name__)


def init_db():
    """
    Initializes the database client and returns a reference to the database.

    Returns:
        pymongo.database.Database: A reference to the database.
    """
    try:
        client = MongoClient(DB_URL, 27017)
        db = client[DB_NAME]
        return db
    except Exception as exception:
        logger.exception("Error initializing database")
        raise exception


def get_collection(db, collection_name: str):
    """
    Returns a reference to the specified collection in the database.

    Args:
        db (pymongo.database.Database): A reference to the database.
        collection_name (str): The name of the collection to retrieve.

    Returns:
        pymongo.collection.Collection: A reference to the specified collection.
    """
    try:
        return db[collection_name]
    except Exception as exception:
        logger.exception("Error getting collection %s", collection_name)
        raise exception


def get_smalltalk():
    """
    Retrieves all smalltalk questions and answers from the database.

    Returns:
        tuple: A tuple containing two lists - one for questions and one for answers.
    """
    try:
        smalltalk = get_collection(DB, "smalltalk")
        docs = smalltalk.find({})
        questions, answers = [], []
        for doc in docs:
            questions.append(doc["question"])
            answers.append(doc["answer"])
        return questions, answers
    except Exception as exception:
        logger.exception("Error getting smalltalk")
        raise exception


def get_qna_lists():
    """
    Retrieves all questions and answers from the database.

    Returns:
        tuple: A tuple containing two lists - one for questions and one for answers.
    """
    try:
        qna = get_collection(DB, "qna")
        docs = qna.find({})
        questions, answers = [], []
        for doc in docs:
            if "answers" not in doc.keys() or "question" not in doc.keys():
                continue
            for answer in doc["answers"]:
                questions.append(doc["question"])
                answers.append(answer)
        return questions, answers
    except Exception as exception:
        logger.exception("Error getting qna")
        raise exception


def find_in_qna(key: str):
    """
    Finds the specified question in the database and returns the associated answers.

    Args:
        key (str): The question to search for.

    Returns:
        list: A list of answers to the specified question.
    """
    qna = get_collection(DB, "qna")
    return qna.find_one({"question": key})["answers"]


def update_vote_qna(vote_type: str, answer: str):
    """
    Updates the vote count for the specified answer in the database.

    Args:
        vote_type (str): The type of vote to update (either 'u' for upvote or 'd' for downvote).
        answer (str): The answer to update the vote count for.
    """
    try:
        qna = get_collection(DB, "qna")
        where_clause = {"answers.answer": answer}
        update_clause = (
            {"$inc": {"answers.$.upvotes": 1}}
            if vote_type == "u"
            else {"$inc": {"answers.$.downvotes": 1}}
        )
        qna.update_one(where_clause, update_clause)
    except Exception as exception:
        logger.exception("Error updating vote count for answer: %s", answer)
        raise exception


global DB
DB = init_db()
