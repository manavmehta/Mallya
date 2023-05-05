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
    try:
        client = MongoClient(DB_URL, 27017)
        db = client[DB_NAME]
        return db
    except Exception as e:
        logger.exception("Error initializing database")
        raise e


def get_collection(db, collection_name):
    try:
        return db[collection_name]
    except Exception as e:
        logger.exception(f"Error getting collection {collection_name}")
        raise e

def get_smalltalk():
    try:
        smalltalk = get_collection(DB, "smalltalk")
        docs = smalltalk.find({})
        questions, answers = [], []
        for doc in docs:
            questions.append(doc["question"])
            answers.append(doc["answer"])
        return questions, answers
    except Exception as e:
        logger.exception("Error getting smalltalk")
        raise e


def get_qna_lists():
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
    except Exception as e:
        logger.exception("Error getting qna")
        raise e


def find_in_qna(key):
    qna = get_collection(DB, "qna")
    return qna.find_one({"question": key})["answers"]

def update_vote_qna(vote_type, answer):
    qna = get_collection(DB, "qna")
    where_clause = {'answers.answer': answer}
    update_clause = {"$inc": {"answers.$.upvotes": 1}} if vote_type == "u" else {"$inc": {"answers.$.downvotes": 1}}
    qna.update_one(where_clause, update_clause) 

global DB
DB = init_db()
