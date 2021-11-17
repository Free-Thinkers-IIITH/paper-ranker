from dblp import fetch_dblp
from flask_mongoengine import MongoEngine
import threading
from app import app
app.config['MONGODB_SETTINGS'] = {
    'db':'dblp',
    'host':'localhost',
    'port':27017
}
db = MongoEngine(app)

#create a new collection for papers
class paper_collection(db.Document):
    pid = db.StringField()
    title = db.StringField()
    year = db.IntField()
    authors = db.ListField(db.StringField())
    venue = db.StringField()
    rank = db.StringField()
    keywords = db.ListField(db.StringField())
    url = db.StringField()
#create a keyword to paper id mapping
class keyword_collection(db.Document):
    keyword = db.StringField()
    papers = db.ListField(db.StringField())

def insert_paper(key,paper_list):
    #insert the papers into the database
    for paper in paper_list:
        pid = paper['id']
        #if id present in papers collection, update keywords
        temp = paper_collection.objects(pid=pid).first()
        if temp:
            #update keywords
            temp.keywords.append(paper['keyword'])
            temp.save()
        else:
            new_paper = paper_collection()
            new_paper.pid = paper['id']
            new_paper.title = paper['title']
            new_paper.year = int(paper['year'])
            new_paper.authors = paper['authors']
            new_paper.venue = paper['venue']
            new_paper.rank = paper['rank']
            new_paper.keywords.append(paper['keyword'])
            new_paper.url = paper['url']
            new_paper.save()
        #update keyword to paper id mapping
        temp = keyword_collection.objects(keyword=str(hash(key))).first()
        if temp:
            temp.papers.append(paper['id'])
            temp.save()
        else:
            new_keyword = keyword_collection()
            new_keyword.keyword = str(hash(key))
            new_keyword.papers.append(paper['id'])
            new_keyword.save()
    
def get_papers(key,hits=30):
    print(key)
    temp = keyword_collection.objects(keyword=str(hash(key))).first()
    if temp:
        print('From DB')
        paper_list = list()
        for pid in temp.papers:
            paper_info = dict()
            temp = paper_collection.objects(pid=pid).first()
            paper_info['title'] = temp.title
            paper_info['year'] = temp.year
            paper_info['authors'] = temp.authors
            paper_info['venue'] = temp.venue
            paper_info['rank'] = temp.rank
            paper_info['url'] = temp.url
            paper_list.append(paper_info)
    else:
        print('From API')
        paper_list = fetch_dblp(key, hits)
        #create a new thread to insert the papers into the database
        t = threading.Thread(target=insert_paper, args=(key,paper_list))
        t.start()
    return paper_list
        

