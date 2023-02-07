from flask import Flask, render_template, redirect, flash, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import string
import random
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

def get_title(url): 
    # making requests instance
    reqs = requests.get(url, headers={"user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0"})
    
    # using the BeautifulSoup module
    soup = BeautifulSoup(reqs.text, 'html.parser')
    
    # displaying the title
    print("Title of the website is : ")
    title = ""
    for i in soup.find_all('title'):
        title = i.get_text()
    return title

def generate_random_string(length=9):
    characters = string.ascii_lowercase
    return ''.join(random.choice(characters) for i in range(length))

#Initialize App
app = Flask(__name__)
app.config['SECRET_KEY'] = "qwujhdiuhei2uhd9283hdiuj2hnd"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://buibaohoang06:Jubm6dXk7BOG@ep-shy-queen-526375.ap-southeast-1.aws.neon.tech/neondb"

#Cors
CORS(app)

#Models
db = SQLAlchemy(app, engine_options={"pool_pre_ping": True})

class Links(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String, nullable=False)
    origin = db.Column(db.String(), nullable=False) #Original link
    output = db.Column(db.String(), nullable=False, unique=True) #Shortened link

#Routes
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/shorten_link', methods=['POST'])
def shorten_link():
    try:
        while True:
            random_url = generate_random_string()
            if Links.query.filter_by(output=random_url).first() == None:
                break
            else: 
                continue
        link = Links()
        #Process link
        link.title = get_title(request.args.get('original'))
        link.origin = request.args.get('original')
        link.output = random_url
        db.session.add(link)
        db.session.commit()
        return jsonify({
            "status": "success",
            "url": random_url
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "danger",
            "error": str(e)
        })

@app.route('/l/<short>', methods=['GET'])
def redirect(short: str):
    try:
        link = Links.query.filter_by(output=short).first()
    except Exception as e:
        print(str(e))
        return abort(404)
    return render_template('redirect.html', link=link.origin, title=link.title)
