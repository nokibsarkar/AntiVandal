from pickle import dump
import re
#import sklearn
import sqlite3 as mysql
import numpy as np
from difflib import SequenceMatcher as seq
from difflib import Differ as diff
from datetime import datetime as dt
from datetime import timedelta as td
import json
diff = diff()
class iterRevisions():
    index = 0
    ref = []
    def __init__(self,X):
        self.index = -1
        self.ref = X
    def __iter__(self):
        return self
    def __next__(self):
        self.index += 1
        try:
            t =  self.ref[self.index]
            pid = t['pageid']
            t=t["revisions"][0]
            return pid, t["user"], t["slots"]["main"]["*"], t["revid"], self.index
        except IndexError:
            raise StopIteration

words = [
 'শেখ'
]
words_len = len(words)
strtype = type('')
now = dt.now()
ISO = "%Y-%m-%dT%H:%M:%SZ"
conn = mysql.connect("Database.db")
cur = conn.cursor()
cur.execute(
	"""CREATE TABLE  IF NOT EXISTS Contents (
		PageID INT PRIMARY_KEY,
		User TEXT DEFAULT NULL,
		Content TEXT DEFAULT NULL,
		RevID INT DEFAULT 0,
		Pointer INT DEFAULT 0
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
    res = x
    x = list(x["query"]["pages"].values())
    l = len(x)
    X = np.zeros((l,100))
    cur.executemany("INSERT INTO Contents (PageID,User,Content,RevID,Pointer) VALUES (?,?,?,?,?)",iterRevisions(x))
    conn.commit()
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
            X[i,96] = 1
            X[i,97] = score(rev['user'],row['title'])
            X[i,98] = score(rev['user'], rev['comment'])
            X[i,99] = len(ill.findall(rev['user']))
    X[:,0] = 1 #Constant or bias value
    pages = res["query"]["pages"]
    del res["query"]["pages"]
    prevs = ','.join(pages.keys())
    prevs = cur.execute("SELECT * FROM Contents WHERE PageID IN (%s)" % prevs)
    #pages = pages.values()
    #users = res['query']['usercontribs']
    for prev in prevs:
        page = pages[str(prev[0])]
        print(page['title'])
        user = prev[1]
        i = prev[4] # row number 
        page =  diff.compare(page['revisions'][0]['slots']['main']['*'], (prev[2]+'x'))
        for j in page:
            #print("index is '%s' " % j[0:2])
            point = 0
            if j[0] is '+':
                point
            elif j[0] is '-':
                point = 1
            else:
                continue
            j = j[2:]
            w = j.split()
            for k in range(words_len):
                if (type(words[k])==strtype):
                    X[i,42 + point * words_len + k] = j.count(words[k])
                else:
                    X[i,42 + point * words_len + k] = sum([1 for m in w if words[k].match(m)])
            if len(w):
                X[i, 42:2 * words_len] *= 1/len(w)

    return X
def fetch():
    X = []
    with open(basepath + 'X.json','r') as fp:
        X = json.loads(fp.read())
    Y = preprocess(
    X#['query']['pages'].values()),
    	)
    with open("data","w") as fp:
        print(Y[:,42:])
        dump(Y,fp)
fetch()
### Database
conn.close()