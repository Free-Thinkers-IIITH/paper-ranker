import urllib.request, json
import pymongo
import json
from pymongo import MongoClient, InsertOne

client = pymongo.MongoClient('mongodb+srv://asxz:asxz@cluster0.4g04r.mongodb.net/ssd?retryWrites=true&w=majority')
db = client.ssd
collection = db.paper
requesting = []

with urllib.request.urlopen('https://dblp.org/search/publ/api?q=machine%20learning&h=10&format=json') as url:
    data = json.loads(url.read().decode())
    requesting.append(InsertOne(data))

result = collection.bulk_write(requesting)
client.close()
