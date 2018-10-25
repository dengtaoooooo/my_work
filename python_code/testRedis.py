from pymongo import MongoClient

conn = MongoClient('127.0.0.1', 27017)
db = conn.duzhe
my_set = db.item
my_set.insert({"hello": "world"})