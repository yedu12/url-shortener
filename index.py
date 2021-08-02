from flask import Flask
import flask 
from flask import render_template,redirect
import re
import random
from string import ascii_letters,digits
import pymongo


def generate_random():
    x = ascii_letters + digits + '+'
    in_list = set(list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"))
    random_ = ''.join(list((random.choice(x) for num in range(5))))
    while random_ in in_list:
        random_ = ''.join(list((random.choice(x) for num in range(5))))
    return random_

app  = Flask(__name__)

@app.route("/",methods= ['GET','POST'])
def index_page():
    if flask.request.method == 'POST':
        host_name = "http://localhost:8080/"
        regex = r"http[s]*:\/\/[www]*\.*.*\..*"
        url = flask.request.form.get("url")
        if re.match(regex,url):
            random =  generate_random()
            client =  pymongo.MongoClient("localhost", 27017)
            db = client.test
            while db.urls.find_one({'key': random}):
                random =  generate_random()
            found = db.urls.find_one({'url': url})
            if found:
                return render_template("index.html",info="Url already has short url <a href=\""+host_name+found.get("key")+"\" >"+host_name+found.get("key")+"</a> <button onclick='copy()'>Copy</button>", url = host_name+found.get("key"))
            db.urls.insert_one({"key":random,"url":url})
            return render_template("index.html",info="Short URL <a href=\""+host_name+random+"\" >"+host_name+random+"</a> <button onclick='copy()'>Copy</button>",url = host_name+random)
        else:
            return render_template("index.html",info="Not a valid url")
    else:
        return render_template("index.html")

@app.route("/<key>", methods = ['GET'])
def routing(key):
    client =  pymongo.MongoClient("localhost", 27017)
    db = client.test
    found = db.urls.find_one({'key': key})
    if found:
        return redirect(found.get("url"), code=302)
    return "URL NOT FOUND"

app.run(debug=True,port=8080)