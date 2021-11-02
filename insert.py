import urllib.request, json
import pymongo
import json
from pymongo import MongoClient, InsertOne

client = pymongo.MongoClient('mongodb+srv://root:root@cluster0.4g04r.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.ssd
collection = db.paper
requesting = []


url = "https://dblp.org/search/publ/api" 
params = { 
    "q": "hashing", 
    "h": "100", 
    "format": "json" 
}     
query_string = urllib.parse.urlencode( params ) 
url = url + "?" + query_string 
 
with urllib.request.urlopen(url) as url_:
    data = json.loads(url_.read().decode())
    requesting.append(InsertOne(data))

result = collection.bulk_write(requesting)
client.close()
