#!/usr/bin/env python3

from pymongo import MongoClient

def initNewDB():
    client = MongoClient('mongodb+srv://manav:e51e3a11@mallya.wwx7jhw.mongodb.net/MallyaDB', 27017)
    db = client['MallyaDB']
    return db

def getCollection(db, collection):
    return db[collection]
# Print the corresponding answer

instance = initNewDB()
