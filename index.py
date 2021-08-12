from os import getenvb
from warnings import catch_warnings
from flask import Flask
import flask 
from flask import render_template,redirect
import re
import random
from string import ascii_letters,digits
import pymongo
import time
from collections import OrderedDict

client = None
cache_f = OrderedDict()
cache_b = OrderedDict()
size = 2


def get_db():
    global client
    if client:
        return client.test
    client =  pymongo.MongoClient("localhost", 27017)
    return client.test
def close_db():
    if client:
        client.close()

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
    global cache_b
    if flask.request.method == 'POST':
        host_name = "http://localhost:8080/"
        regex = r"http[s]*:\/\/[www]*\.*.*\..*"
        url = flask.request.form.get("url")
        if re.match(regex,url):
            random =  generate_random()
            db = get_db()
            if url in cache_b:
                print("Found in cache")
                return render_template("index.html",info="Url already has short url <a href=\""+host_name+cache_b[url]+"\" >"+host_name+cache_b[url]+"</a> <button onclick='copy()'>Copy</button>", url = host_name+cache_b[url])
            found = db.urls.find_one({'url': url})
            if found:
                cache_b[url] = found.get("key")
                return render_template("index.html",info="Url already has short url <a href=\""+host_name+found.get("key")+"\" >"+host_name+found.get("key")+"</a> <button onclick='copy()'>Copy</button>", url = host_name+found.get("key"))
            while db.urls.find_one({'key': random}):
                random =  generate_random() 
            db.urls.insert_one({"key":random,"url":url})
            return render_template("index.html",info="Short URL <a href=\""+host_name+random+"\" >"+host_name+random+"</a> <button onclick='copy()'>Copy</button>",url = host_name+random)
        else:
            return render_template("index.html",info="Not a valid url")
    else:
        return render_template("index.html")

# def insert_to_cache(key,url):
#     global cache_f,size
#     timestamp = int(time.time())
#     if len(cache_f) < size:
#         cache_f[key] = {"url":url, 'timestamp':timestamp}
#     old = cache_f[list(cache_f.keys())[0]]
#     old_key = list(cache_f.keys())[0]
#     for i in cache_f.keys():
#         if old['timestamp'] > cache_f[i]['timestamp']:
#             old = cache_f[i]
#             old_key = i
#     del cache_f[old_key]
#     cache_f[key] = {"url":url, 'timestamp':timestamp}
#     print(cache_f)

@app.route("/<key>", methods = ['GET'])
def routing(key):
    global cache_f
    db = get_db()
    if key in cache_f:
        cache_f.move_to_end(key)
        return redirect(cache_f[key], code=302)
    found = db.urls.find_one({'key': key})
    if found:
        cache_f[key] = found.get('url')
        cache_f.move_to_end(key)
        return redirect(found.get("url"), code=302)
    return "URL NOT FOUND"

app.run(debug=True,port=8080)