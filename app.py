#!/usr/bin/env python3

from flask import Flask, request, Response, render_template
from flask_cors import CORS, cross_origin
import os
app = Flask(__name__)

@app.route('/deploy/<string:token>')
def deploy(token):
    if token == "DEPLOY_TOKEN":
        os.system('cd ~/www/python/src && git pull && webservice restart > ~/nokib.log 2>&1 &')
        return "Deployed!"
    else:
        return Response(status=404)






@app.post("/sample/<int:user_id>")
@cross_origin(origins="*")
def collect_sample(user_id):
    return str(user_id)


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
    app.run()