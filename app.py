#!/usr/bin/env python3

from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
import os
app = Flask(__name__)

@app.route('/deploy/<string:token>')
def deploy(token):
    if token == os.environ.get('DEPLOY_TOKEN'):
        os.system('git pull')
        os.system('pip install -r requirements.txt')
        return Response(status=200)
    else:
        return Response(status=403)

@app.post("/sample/<int:user_id>")
@cross_origin(origins="*")
def collect_sample(user_id):
    return str(user_id)


@app.route('/')
def home():
    return "Hello World!"

if __name__ == '__main__':
    app.run()