# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from difflib import  unified_diff as diff
import sqlite3, json
from requests import Session
from xml.etree import ElementTree as XML
#conn = None
if 'conn' in dir():
  print('Previous Database Closed')
  conn.close()
conn = sqlite3.connect('database.db')
cur = conn.cursor()

# %% [markdown]
# The Features we'll be saving as follows:
# - Title of the page
# - comment of the edit
# - revision ID of the current and previous edit
# - difference of the content
# - Username or IP
# 
# Because these can be hiiden by an admin.

# %%
SQL_INIT = """
CREATE TABLE IF NOT EXISTS `Revisions` (
  `RevID` INTEGER PRIMARY KEY,
  `Title` TEXT NOT NULL,
  `ParentID` INTEGER NULL DEFAULT NULL,
  `Comment` TEXT NULL DEFAULT NULL,
  `Anonymous` BOOLEAN DEFAULT FALSE,
  `Editor` VARCHAR(90) NULL DEFAULT NULL,
  `Text` TEXT NULL DEFAULT NULL,
  `Deleted` BOOLEAN DEFAILT FALSE
) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS `ParentID` ON `Revisions`(`ParentID`);
CREATE TABLE IF NOT EXISTS `Labels` (
  `RevID` INTEGER REFERENCES `Revisions` (`RevID`),
  `Labeller` VARCHAR(100) NOT NULL,
  `Vandalism` BOOLEAN DEFAULT FALSE,
  `Timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
SQL_INSERT_REVISION = """
INSERT INTO `Revisions`
  (`Title` ,`RevID`, `ParentID`, `Comment`, `Anonymous`, `Editor`, `Deleted`, `Text`)
VALUES
  (?, ?,?,?,?,?,?, ?);
"""
SQL_UPDATE_REVISION = """
UPDATE `Revisions` SET `Text` = ? WHERE `ParentID` = ?
"""
cur.executescript(SQL_INIT)


# %%
# the parameter to pass on
mw = 'http://www.mediawiki.org/xml/export-0.11/' #The namespace
api_endpoint = 'https://bn.wikipedia.org/w/api.php' #Wikipedia API endpoint
ses = Session()
cache={}
insert_list = set()
backlog = set() # The Parent IDs which should be fetched
params_live = {
	"action": "query",
	"format": "json",
	"prop": "revisions",
	"utf8": 1,
  "indexpageids":1,
	"rvprop": "comment|content|ids|flags|user",
	"rvslots": "main"
}


# %%
def process_batch(query={}, ids=[], cache={}):
  """This function will be called on update statement each batch of results
  `queries`: The list of the values
  `cache`: A dictionary with `ParentID` as key and `Current revision` as Value
  """
  global backlog
  for id in ids:
    page = query[id]
    if 'revisions' not in page:
      print('Revision not found', page['title'])
      continue
    title = page['title']
    revision = page['revisions'][0]
    current_text = revision['slots']['main']['*'].splitlines()
    current_id = revision['revid']
    parent_id = revision['parentid']
    comment = revision['comment']
    editor = revision['user']
    insertable_text = None
    print(f'current Backlog size : {len(backlog)}')
    backlog.discard(current_id)
    print(f'current Backlog size : {len(backlog)}')
    if current_id in cache:
      print("""Put the difference""")
      insertable_text = '\n'.join(diff(cache[current_id], current_text))
      del cache[current_id]
      # if parent_id:
      #   # Add parent to the backlog
      #   backlog.add(parent_id)'
      #   print('Push to cache')
      #   cache[parent_id] = current_text
      print('Update parameters')
      yield insertable_text, current_id
    else:
      print(f'cache[{current_id}] not found', title)
      if not parent_id:
        print('First Revision', title)
        """
        ParentID does not exist
        So this is the first revision
        Insert it in raw format
        """
        parent_id = None
        insertable_text = '\n'.join(diff('', current_text))
      else:
        cache[parent_id] = current_text
        backlog.add(parent_id)
      #Insert into database
      insert_list.add(
          (
          title,
          current_id, parent_id,
          comment, 1, editor, 1,
          insertable_text)
      )


# %%
def fetch(ids = [], last_time = 0, grccontinue=None, rvcontinue=None, limit=100, idlimit=50):
  global cache, insert_list, backlog
  k=10
  while k:
    print('Epoch', k)
    if grccontinue:
      print('Generator Continuation')
      data = {**params_live,
        "generator": "recentchanges",
        "grcstart": last_time,
        "grcdir": "newer",
        "grclimit": limit,
        "grctoponly": 1,
        'grccontinue' : grccontinue
      }
    elif ids:
      ids = list(map(str, backlog.union(ids)))
      next_ids = []
      if len(ids) > idlimit:
        next_ids, ids = ids[idlimit:], ids[:idlimit]
      print('Current ID given', len(ids))
      data = {**params_live, 'revids':'|'.join(ids)}
      ids = next_ids
      print('Revision IDs are Given', data['revids'])
    elif last_time:
      print('Fetching Live Changes')
      data = {**params_live,
        "generator": "recentchanges",
        "grcstart": last_time,
        "grcdir": "newer",
        "grclimit": limit,
        "grctoponly": 1
      }
    else:
      print('neither Last Time nor Revision ID defined')
      
    if rvcontinue:
      # Revision continual
      data['rvcontinue'] = rvcontinue
    res = ses.post(api_endpoint, params=data, headers={'content-type':'application/json'}).json()
    
    if 'query' not in res:
      print('Query Not found')
      print(res)
      return
    cur.executemany(SQL_UPDATE_REVISION, process_batch(ids=res['query']['pageids'], query=res['query']['pages'], cache=cache))
    for i in insert_list:
      try:
        cur.execute(SQL_INSERT_REVISION, i)
      except sqlite3.IntegrityError as e:
        print(f'Error {i[0]}')
        pass
    insert_list = set()
    if 'continue' in res:
      print('Continual', res['continue'])
      grccontinue = res['continue']['grccontinue']
    if backlog:
      ids = backlog
    k -= 1
  
#cache={}
# fetch(ids=[123456, 123457]))
fetch(last_time='2021-08-28T07:34:00.000Z')


# %%
#cur.execute('DELETE FROM Revisions')
for i in cur.execute('SELECT * FROM Revisions LIMIT 1'):
    print(i)
#print(cache)


# %%
print(insert_list)


# %%



# %%
cache


