#!/usr/bin/env python3

from flask import Flask, request, Response, render_template, g
from flask_cors import CORS, cross_origin
import os, sqlite3
from collect_data import collect_sample, WikiSession, SQL_INIT
app = Flask(__name__)
CORS(app, resources={
    "/sample/*": {
        "origins": "https://bn.wikipedia.org",
        "methods": ["POST", "OPTIONS"]
    }
})
@app.route('/deploy/<string:token>')
def deploy(token):
    if token == "DEPLOY_TOKEN":
        os.system('cd ~/www/python/src && git pull && webservice restart > ~/nokib.log 2>&1 &')
        return "Deployed!"
    else:
        return Response(status=404)



DATABASE_INIT = False

@app.before_request
def before_request():
    g.db = sqlite3.connect("data.db")
    global DATABASE_INIT
    if not DATABASE_INIT:
        WikiSession.init()
        g.db.executescript(SQL_INIT)
        g.db.commit()
        DATABASE_INIT = True
@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.post("/sample/<int:user_id>")
def collect_samples(user_id):
    data = request.get_json()
    if 'positivs' not in data:
        positives = []
        len_positives = len(data['positive'])
        for i in range(0, len_positives, 2):
            positives.append((data['positive'][i], data['positive'][i+1]))
        collect_sample(g.db, user_id, positives, 'good')


    if 'negative' in data:
        negatives = []
        len_negatives = len(data['negative'])
        for i in range(0, len_negatives, 2):
            negatives.append((data['negative'][i], data['negative'][i+1]))
        collect_sample(g.db, user_id, negatives, 'bad')
    return {'success' : True}


@app.get('/subscribe')
def subscription_details():
    return render_template('subscribe.html')

@app.post('/subscribe')
def subscribe():
    return "Subscribed"


@app.get('/unsubscribe/<string:token>')
def unsubscribe_details():
    return render_template('unsubscribe.html')

@app.post('/unsubscribe/<int:user_id>')
def unsubscribe(user_id):
    return str(user_id)
@app.route('/terms')
def terms():
    return render_template('terms.html')













@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)