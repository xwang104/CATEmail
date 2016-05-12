from pymongo import MongoClient
db = MongoClient().catemail
collection = db.messages
maxTime = collection.find_one(sort=[("timestamp", -1)])
print maxTime
