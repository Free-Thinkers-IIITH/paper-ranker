import threading
from flask import Flask, render_template, request, url_for
from fetch import fetch_from_db
from user_management import User
from insert_paper import insert_paper
from dblp import fetch_dblp
import time
from flask_paginate import Pagination, get_page_args
import threading
from flask_mongoengine import MongoEngine


app = Flask(__name__)
app.secret_key = "hi there"
user = User()

current_theme = 1

conferences = [{"publisher": "IEEE"}, {"publisher": "IOS Press"}, {
    "publisher": "IEEE Computer Society"}, {"publisher": "Springer"}]

topics = [{"subject": "Machine Learning"}, {
    "subject": "Cyber Security"}, {"subject": "Internet of things"}]

# -----------------------------------DATABASE-----------------------------------
app.config['MONGODB_SETTINGS'] = {
    'db': 'dblp',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine(app)

# create a new collection for papers


class paper_collection(db.Document):
    pid = db.StringField()
    title = db.StringField()
    year = db.IntField()
    authors = db.ListField(db.StringField())
    venue = db.StringField()
    rank = db.StringField()
    keywords = db.ListField(db.StringField())
    url = db.StringField()
# create a keyword to paper id mapping


class keyword_collection(db.Document):
    keyword = db.StringField()
    papers = db.ListField(db.StringField())


def insert_paper(key, paper_list):
    # insert the papers into the database
    for paper in paper_list:
        pid = paper['id']
        # if id present in papers collection, update keywords
        temp = paper_collection.objects(pid=pid).first()
        if temp:
            # update keywords
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
        # update keyword to paper id mapping
        temp = keyword_collection.objects(keyword=str(hash(key))).first()
        if temp:
            temp.papers.append(paper['id'])
            temp.save()
        else:
            new_keyword = keyword_collection()
            new_keyword.keyword = str(hash(key))
            new_keyword.papers.append(paper['id'])
            new_keyword.save()
    print('Insertion Completed!')

def get_papers(key, hits=30):
    temp = keyword_collection.objects(keyword=str(hash(key))).first()
    if temp:
        start = time.time()
        print(f'fetching {key} papers From DB')
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
        end = time.time()
        print(f'Total {len(paper_list)} papers fetched in {end-start} seconds')
    else:
        print(f'fetching {key} papers From API')
        start = time.time()
        paper_list = fetch_dblp(key, hits)
        end = time.time()
        print(f'Total {len(paper_list)} papers fetched in {end-start} seconds')
        print('New thread is inserting to db')
        # create a new thread to insert the papers into the database
        t = threading.Thread(target=insert_paper, args=(key, paper_list))
        t.start()
    return paper_list

# -----------------------------------DATABASE-----------------------------------


@app.route('/')
def index():
    return render_template('index.html', theme=current_theme)


@app.route('/login')
def login():
    return render_template('login.html', theme=current_theme)


@app.route('/login/ans', methods=['POST', 'GET'])
def login_ans():
    user.logout()
    name = request.form['username']
    pwd = request.form['password']
    a = user.login(name, pwd)
    if a == 1:
        return render_template('org_insertion.html', theme=current_theme)
    elif a == -1:
        return render_template('org_insertion.html', theme=current_theme)
    elif a == -2:
        return render_template('login.html', info="invalid username")
    elif a == -3:
        return render_template('login.html', info="invalid password")
    elif a == -4:
        return render_template('login.html', info="another user is  logged in")


# @app.route('/register')
# def show_regeistration_page():
#     return render_template('register.html')


@app.route('/register_in', methods=['POST', 'GET'])
def register_user():
    a = user.register(request.form['username'], request.form['password'],
                      request.form['email'], request.form['department'])
    if a == 1:
        return render_template('login.html')
    elif a == -1:
        return "username taken"
    elif a == -2:
        return "email taken"


@app.route('/register')
def register():
    return render_template('registration.html', theme=current_theme)


@app.route('/register/ans', methods=['POST', 'GET'])
def register_ans():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    department = request.form['department']
    check = user.register(username, password, email, department)
    if check == -1:
        return render_template(
            'registration.html',
            info='Username already exixsts!')
    elif check == -2:
        return render_template(
            'registration.html',
            info='Email already exists!')
    else:
        return render_template(
            'registration.html',
            info="Registered successfully !!!!")


posts = []


def get_posts(offset=0, per_page=10):
    return posts[offset: offset + per_page]


@app.route('/search', methods=['POST', 'GET'])
def search():
    query = request.form['search_query']
    posts = get_papers(query, 1000)
    return render_template(
        'home.html',
        posts=posts,
        title="Paper Ranker",
        theme=current_theme,
        conferencesList=conferences,
        topicList=topics)


@app.route('/org_insertion', methods=['POST', 'GET'])
def org_insertion():
    if(user.check()):
        details = dict()
        details['title'] = request.form['title']
        details['authors'] = request.form['authors'].split(',')
        details['venue'] = request.form['venue']
        details['year'] = request.form['year']
        details['access'] = request.form['access']
        details['url'] = request.form['url']
        details['rank'] = request.form['rank']
        details['keywords'] = request.form['field'].split(',')
        # print(details)
        insert_paper(details)
        return render_template('org_insertion.html', theme=current_theme)

    else:
        return render_template('login.html', info='You are not logged in')


@app.route('/logout')
def log_out():
    user.logout()
    return render_template('login.html', theme=current_theme)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
