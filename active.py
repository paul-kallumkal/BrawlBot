from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
  return "Server active"

def run():
  app.run(host='0.0.0.0',port=8080)

def active():
  t= Thread(target=run)
<<<<<<< HEAD
  t.start()

=======
  t.start()
>>>>>>> 4e61ae53a33806e55088cd41b46dc99e5cc18d94
