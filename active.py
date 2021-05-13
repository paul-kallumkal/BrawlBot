from flask import Flask,request,render_template
from threading import Thread
from functions import link_steam

app = Flask('')

@app.route('/')
def home():
  return "Server active"

@app.route('/login')
def login():
  return render_template('steam.html',message=link_steam(request.args.get("code")))

def run():
  app.run(host='0.0.0.0',port=8080)

def active():
  t= Thread(target=run)
  t.start()