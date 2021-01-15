#!/usr/bin/env python3

import gspread
from pymongo import MongoClient
client = MongoClient()

gc = gspread.service_account()
client = MongoClient('localhost', 27017)

print('\nFetching Questions...\n')
sht = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Jged2Bis3KymVCfBqdaSUf6mJZm0iJDWai3QxtrkLHQ/edit#gid=0')
worksht = sht.get_worksheet(0)
qna_dict = worksht.get_all_records()
print('\nQuestions fetched succesfully !\n')

db = client['mallya']

collection_questions = db['questions']
collection_answers = db['answers']

collection_questions.drop()
collection_answers.drop()


for obj in qna_dict:

    ques = obj['Question']
    ans = obj['Answer']

    ans_list_id = []
    
    if ans != '' and (not ans.isspace()):
        ans_list_json = [{'text': a, 'upvotes': [], 'downvotes': [], 'score': 0} for a in ans.split('&&')]
        ans_list_id = collection_answers.insert_many(ans_list_json).inserted_ids

    ques_json = {'text': ques, 'answers': ans_list_id}
    ques_id = collection_questions.insert_one(ques_json)