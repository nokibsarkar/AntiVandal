#!/usr/bin/env python3

from flask import Flask, request, Response, render_template, g, send_file
from flask_cors import CORS, cross_origin
import os, sqlite3, re
PRE_PATTERN = re.compile('<pre>(.*?)</pre>', re.DOTALL)
from collect_data import collect_sample, WikiSession, SQL_INIT, get_revisions, get_labels
app = Flask(__name__)
CORS(app, resources={
    "/sample/*": {
        "origins": ["https://bn.wikipedia.org", "https://bn.m.wikipedia.org"],
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
    g.db.row_factory = sqlite3.Row
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

@app.get('/download')
def download():
    return send_file('data.db', as_attachment=True)
@app.get('/sample')
def samples():
    limit = request.args.get('limit', 100)
    offset = request.args.get('offset', 0)
    if limit:
        limit = int(limit)
    if offset:
        offset = max(int(offset), 0)
    revisions = get_revisions(g.db, offset, limit)
    if len(revisions) > 0:
        next_url = f'/sample?limit={limit}&offset={offset+limit}'
    else:
        next_url = None
    if offset > limit:
        prev_url = f'/sample?limit={limit}&offset={offset-limit}'
    else:
        prev_url = None
    return render_template('sample.html', revisions = revisions, PRE_PATTERN=PRE_PATTERN, next_url=next_url, prev_url=prev_url)

@app.post("/sample/<int:user_id>")
def collect_samples(user_id):
    data = request.get_json()
    if 'positive' in data:
        collect_sample(g.db, user_id, map(int, data['positive']), 'good')
    if 'negative' in data:
        collect_sample(g.db, user_id, map(int, data['negative']), 'bad')
    return data


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