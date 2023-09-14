#!/usr/bin/env python3

from flask import Flask, request, Response
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


@app.route('/')
def home():
    return "Hello World!"

if __name__ == '__main__':
    app.run()