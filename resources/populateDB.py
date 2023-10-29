import sys

sys.path.append("..")
from db import *
from pprint import pprint


def restructureQnA():
    collection = get_collection(DB, "qna")
    all_documents = collection.find()

    # create a dictionary to store combined questions and answers
    question_answer_dict = {}
    # collection.delete_many({})
    # loop through each document
    for document in all_documents:
        # get the question and answer from the current document
        question = document["question"]
        answer = document["answer"]

        # if the question is not in the dictionary, add it
        if question not in question_answer_dict:
            question_answer_dict[question] = {
                "_id": document["_id"],
                "question": question,
                "answers": [answer],
            }
        else:
            # if the question is already in the dictionary, add the answer to the list of answers
            question_answer_dict[question]["answers"].append(answer)

    # convert the dictionary to a list of documents
    combined_documents = list(question_answer_dict.values())

    # update the documents to add upvotes and downvotes to each answer
    for document in combined_documents:
        for answer_index, answer in enumerate(document["answers"]):
            document["answers"][answer_index] = {
                "answer": answer,
                "upvotes": 0,
                "downvotes": 0,
            }
    pprint(combined_documents)
    # insert the updated documents into the collection
    collection.delete_many({})
    collection.insert_many(combined_documents)


restructureQnA()
