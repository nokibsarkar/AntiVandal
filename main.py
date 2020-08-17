import re
import sqlite3 as mysql
import numpy as np
from difflib import SequenceMatcher as seq
from datetime import datetime as dt
from datetime import timedelta as td
import json
now = dt.now()
ISO = "%Y-%m-%dT%H:%M:%SZ"
conn = mysql.connect("Database.db")
cur = conn.cursor()
cur.execute(
	"""CREATE TABLE  IF NOT EXISTS Antivandal (
		ID INT PRIMARY_KEY AUTO INCREMENT,
		User TEXT DEFAULT NULL,
		Title TEXT DEFAULT NULL,
		Content TEXT DEFAULT NULL,
		PreviousID INT DEFAULT 0,
		Tags JSON DEFAULT NULL
		) ;"""
	)
conn.commit()
def score(s1,s2):
    return seq(None,s1,s2).ratio()
ill = None
basepath = '/storage/emulated/0/qpython/scripts/'
with open(basepath + 'illegal_username.txt','r') as fp:
    ill = re.compile(
    	fp.read(),
    	re.I | re.U
    	)
def preprocess(x):
    l = len(x)
    X = np.zeros((l,100))
    for i in range(l):
        row = x[i]
        rev = row['revisions'][0]
        X[i,1 + row['ns']] = 1 #namespace
        X[i,16] = (rev['revid'] - rev['parentid'])
        X[i,17] = (dt.strptime(rev['timestamp'],ISO) - dt.strptime(row['touched'],ISO)).seconds
        X[i, 18] = '/' in row['title']#is on subpage
        X[i,19] = 'mw-rollback' in rev['tags']
        X[i,20] = 'mw-undo' in rev['tags'] or 'mw-manual-revert' in rev['tags']
        X[i,21] = 'আলাপ পাতা খালি করা হয়েছে!' in rev['tags']
        X[i,22] = 'mw-new-redirect' in rev['tags'] or 'mw-changed-changed-target' in rev['tags']
        X[i,23] = 'অন্য ব্যবহারকারীর পাতা তৈরি' in rev['tags']
        X[i,24] = 'অত্যন্ত সংক্ষিপ্ত নতুন নিবন্ধ' in rev['tags']
        X[i,25] = 'visualeditor' in rev['tags']
        X[i,26] = 'visualeditor-wikitext' in rev['tags']
        X[i,27] = 'mw-removed-redirect-target' in rev['tags'] 
        X[i,28] = 'ব্যবহারকারী আত্মজীবনী তৈরি করেছেন' in rev['tags']
        X[i,29] = 'বাংলা নয় এমন বিষয়বস্তু অতি মাত্রায় যোগ' in rev['tags']
        X[i,30] = 'mw-replace' in rev['tags']
        X[i,31] = 'mw-blank' in rev['tags'] or 'blanking' in rev['tags']
        X[i,32] = 'নতুন ব্যবহারকারী বহিঃসংযোগ যুক্ত করেছেন' in rev['tags']
        ####--নতুন ব্যবহারকারী দ্রুত অপসারণ ট্যাগ বাতিল করেছেন
        X[i,33] = 'নতুন ব্যবহারকারী দ্রুত অপসারণ ট্যাগ বাতিল করেছেন' in rev['tags']
        X[i,34] = 'নতুন ব্যবহারকারী পাতা খালি করেছেন!' in rev['tags'] or 'mw-manual-revert' in rev['tags']
        X[i,35] = 'আলাপ পাতা খালি করা হয়েছে!' in rev['tags']
        X[i,36] = 'emoji' in rev['tags'] or 'mw-changed-changed-target' in rev['tags']
        X[i,37] = 'অনুচ্ছেদ খালি করা হয়েছে' in rev['tags']
        X[i,38] = 'তথ্য অপসারণ' in rev['tags']
        X[i,39] = 'চিত্রের বিবরণ বাংলা নয়' in rev['tags']
        X[i,40] = 'অস্বাভাবিক পুনর্নির্দেশ' in rev['tags']
        X[i,41] = rev['size']/1e3
        #-----Title featuring -----#
        X[i,42] = len(ill.findall(row['title']))
        # Comment featuring
        #---- Content features ----#
        # compare with previous
        ## tla = total link added
        ## tlr = total link removed
        ## tea = total external link added
        ## ter = total external link removed
        ## tea/tla
        ## ter/tlr
        ## trl = total removed line
        ## tal = total added line
        ## twr = total word removed
        ## twa = total word added
        ## slangs in added lines
        ## 
        if 'anon' not in rev:
            X[i,52] = 1
            X[i,53] = score(rev['user'],row['title'])
            X[i,54] = score(rev['user'], rev['comment'])
            X[i,55] = len(ill.findall(rev['user']))
    X[:,0] = 1 #Constant or bias value
    return X
def featureContent()
def fetch():
    X = []
    with open(basepath + 'X.json','r') as fp:
        X = json.loads(fp.read())
    print(preprocess(
    	list(X['query']['pages'].values()),
    	)[:,27:42])
fetch()
### Database
conn.close()