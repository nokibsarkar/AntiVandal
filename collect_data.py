from difflib import unified_diff as diff
import sqlite3
from requests import Session
from datetime import datetime
from time import sleep
if 'conn' in dir():
    print('Previous Database Closed')
    conn.close()
conn = sqlite3.connect('database.db')
cur = conn.cursor()
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
mw = 'http://www.mediawiki.org/xml/export-0.11/'  # The namespace
api_endpoint = 'https://bn.wikipedia.org/w/api.php'  # Wikipedia API endpoint
ses = Session()
cache = {}
insert_list = set()
backlog = set()  # The Parent IDs which should be fetched
revision_backlog = set()

params_live = {
    "action": "query",
    "format": "json",
    "prop": "revisions",
    "utf8": 1,
    "indexpageids": 1,
    "rvprop": "comment|content|ids|flags|user|timestamp",
    "rvslots": "main"
}
total = 0
suceed = set()
success = 0


def process_batch(query={}, ids=[], cache={}, last_time=0):
    """This function will be called on update statement each batch of results
    `queries`: The list of the values
    `cache`: A dictionary with `ParentID` as key and `Current revision` as Value
    """
    print('\t\t\t\t\Current Timestamp : ', last_time.isoformat())
    global backlog, revision_backlog, success, total, suceed
    for id in ids:
        total += 1
        page = query[id]
        print(page['title'])
        if 'revisions' not in page:
            revision_backlog.add(page['title'])
            print('\tRevision not found')
            continue
        success += 1
        if page['title'] in revision_backlog:
            print('\t\t', page['title'], 'Revived')
            revision_backlog.remove(page['title'])
        title = page['title']
        suceed.add(title)
        revision = page['revisions'][0]
        try:
          current_text = revision['slots']['main']['*'].splitlines()
        except Exception as e:
          print('\tError : %s' % e)
          current_text = ''
        current_id = revision['revid']
        parent_id = revision['parentid']
        try:
          comment = revision['comment']
        except Exception as e:
          print('\tError : %s' % e)
          comment = None
        try:
          editor = revision['user']
        except Exception as e:
          print('\tError : %s' % e)
          editor = None
        timestamp = datetime.fromisoformat(revision['timestamp'][:-1])
        print(f'{timestamp} > {last_time} : {timestamp > last_time}')
        if timestamp > last_time:
            last_time = timestamp
            print('\t\t\t\t\tCurrent Timestamp : ', timestamp.isoformat())
        insertable_text = None

        backlog.discard(current_id)
        print(f'\tBacklog size : {len(backlog)}')
        success = +1
        if current_id in cache:
            print("""\tPut the difference""")
            insertable_text = '\n'.join(diff(current_text, cache[current_id]))
            del cache[current_id]
            print('\tUpdate parameters')
            yield insertable_text, current_id
        else:
            print(f'\tcache[{current_id}] not found')
            if not parent_id:
                print('\tFirst Revision', title)
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
            insert_list.add(
                (
                    title,
                    current_id, parent_id,
                    comment, 1, editor, 1,
                    insertable_text)
            )


def fetch(
    ids=[],
    last_time=datetime.utcnow(),
    grccontinue=None,
    rvcontinue=None,
    limit=50,
    idlimit=50,
    rate=60/40
):
    global cache, insert_list, backlog
    k = 5
    cont = None
    while k:
        print('Epoch', k)
        if cont:
            print('\t\tContinue---------------------', success, total)
            data = {**params_live,
                    "generator": "recentchanges",
                    "grcstart": last_time,
                    "grcdir": "newer",
                    "grclimit": limit,
                    "grctoponly": 1,
                    'continue': cont,
                    'grctag': 'mw-rollback'
                    }
            if grccontinue:
                data['grccontinue'] = grccontinue
            if rvcontinue:
                data['rvcontinue'] = rvcontinue
        elif ids:
            ids = list(map(str, backlog.union(ids)))
            next_ids = []
            if len(ids) > idlimit:
                next_ids, ids = ids[idlimit:], ids[:idlimit]
            data = {**params_live, 'revids': '|'.join(ids)}
            ids = next_ids
        elif last_time:
            print('Fetching Live Changes')
            if isinstance(last_time, str):
                last_time = datetime.fromisoformat(last_time)
            data = {**params_live,
                    "generator": "recentchanges",
                    "grcstart": last_time.isoformat(timespec='seconds'),
                    "grcdir": "newer",
                    "grclimit": limit,
                    "grctoponly": 1,
                    'grctag': 'mw-rollback'
                    }
        else:
            print('neither Last Time nor Revision ID defined')

        res = ses.post(
            api_endpoint,
            params=data,
            headers={
                'content-type': 'application/json'}).json()
        if 'query' not in res:
            print('Query Not found')
            print(res)
            return
        print(data)
        cur.executemany(SQL_UPDATE_REVISION, process_batch(
            ids=res['query']['pageids'],
            query=res['query']['pages'],
            cache=cache,
            last_time=last_time
        ))
        for i in insert_list:
            try:
                cur.execute(SQL_INSERT_REVISION, i)
            except sqlite3.IntegrityError as e:
                print(f'Error {i[0]}')
                backlog.discard(i[1])
                pass
        insert_list = set()
        if 'continue' in res:
            cont = res['continue']['continue']
            print('Continual', res['continue'])
            if 'grccontinue' in res['continue']:
                grccontinue = res['continue']['grccontinue']
            else:
                grccontinue = None
            if 'rvcontinue' in res['continue']:
                rvcontinue = res['continue']['rvcontinue']
            else:
                rvcontinue = None
        else:
            cont = None
        if backlog:
            ids = backlog
        k -= 1

        print(
            f'Success Rate : {len(suceed)} / {total}  = {len(suceed) * 100/ total : 0.2f}%')
        print(' \tSleeping ------------------------------------')
        with open('time.txt', 'w') as fp:
            fp.write(last_time.isoformat())
        sleep(rate)
if __name__ == '__main__':
  try:
    last_time : datetime = datetime.fromisoformat('2021-07-28T00:00:00')
    print(last_time)
    """
    This script will be used for grabbing the rollbacks from wikipedia
    """
    # with open('time.txt', 'r') as fp:
    #   last_time = datetime.fromisoformat(fp.read())
    fetch(last_time=last_time)
  except Exception as e:
    # Id = 1
    print('Error Happened : %s' % e)
    print('Exiting....................')
