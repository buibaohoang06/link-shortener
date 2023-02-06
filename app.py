from flask import Flask, render_template, redirect, flash, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import string
import random
from flask_cors import CORS
from urllib.request import urlopen
from bs4 import BeautifulSoup

def generate_random_string(length=9):
    characters = string.ascii_lowercase
    return ''.join(random.choice(characters) for i in range(length))

#Initialize App
app = Flask(__name__)
app.config['SECRET_KEY'] = "testkey"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

#Cors
CORS(app)

#Models
db = SQLAlchemy(app)

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
        soup = BeautifulSoup(urlopen(request.args.get('original')))
        link.title = soup.title.get_text()
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
        return abort(404)
    return render_template('redirect.html', link=link.origin, title=link.title)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)