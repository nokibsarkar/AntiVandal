import sqlite3
from datetime import datetime
from time import sleep
from requests import Session
from settings import OAUTH_ACCESS_TOKEN
SQL_INIT = """
CREATE TABLE IF NOT EXISTS `Revisions` (
    `id` INTEGER PRIMARY KEY,
    `title` TEXT NOT NULL,
    `ns` INTEGER NOT NULL,
    `diff` TEXT NULL DEFAULT NULL,
    `parent_id` INTEGER NULL DEFAULT NULL,
    `comment` TEXT NULL DEFAULT NULL,
    `editor` TEXT NULL DEFAULT NULL,
    `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `is_diff` BOOLEAN DEFAULT FALSE
) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS `parent_id` ON `Revisions`(`parent_id`);
CREATE TABLE IF NOT EXISTS `Labels` (
    `rev_id` INTEGER REFERENCES `Revisions` (`id`),
    `labeller` VARCHAR(100) NOT NULL,
    `label` VARCHAR(100) NOT NULL,
    `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
_SQL_INSERT_REVISION = """
INSERT INTO `Revisions`
    (`id`, `title`, `ns`, `diff`, `parent_id`, `comment`, `editor`, `timestamp`, `is_diff`)
VALUES
    (:id, :title, :ns, :diff, :parent_id, :comment, :editor, :timestamp, :is_diff);
"""
_SQL_INSERT_LABEL = """
INSERT INTO `Labels`
    (`rev_id`, `labeller`, `label`)
VALUES
    (:rev_id, :labeller, :label);
"""
_SQL_FETCH_REVISION_BY_ID = """
SELECT `id` FROM `Revisions` WHERE `id` = :id;
"""
class WikiSession:
    session = Session()
    BNWIKI_API_URL = 'https://bn.wikipedia.org/w/api.php'
    last_time = 0
    interval = 1
    @staticmethod
    def init():
        WikiSession.session.headers.update({
            "User-Agent": "",
            "Accept": "application/json",
            "Authorization": "Bearer " + OAUTH_ACCESS_TOKEN
        })
        WikiSession.session.params.update({
            "format": "json",
            "utf8": "1"
        })
        WikiSession.session
    @staticmethod
    def get(params={}):
        now = datetime.now().timestamp()
        sleeping_time = WikiSession.interval - (now - WikiSession.last_time)
        if sleeping_time > 0:
            print('Sleeping for %f seconds' % sleeping_time)
            sleep(sleeping_time)
        return WikiSession.session.get(WikiSession.BNWIKI_API_URL, params=params).json()
    @staticmethod
    def post(data={}):
        now = datetime.now().timestamp()
        sleeping_time = WikiSession.interval - (now - WikiSession.last_time)
        if sleeping_time > 0:
            print('Sleeping for %s seconds' % sleeping_time)
            sleep(sleeping_time)
        
        return WikiSession.session.post(WikiSession.BNWIKI_API_URL, data=data).json()
    
def _calculate_diff(newer_revid):
    result = {
        'title' : None,
        'ns' : None,
        'diff': None,
        'id': None,
        'parent_id': None,
        'comment': None,
        'editor': None,
        'timestamp': None,
        'is_diff': True
    }
    data = {
        "action": "compare",
        "format": "json",
        # "assertuser": "Nokib Sarkar",
        "fromrev": newer_revid,
        "torelative" : "prev",
        "prop": "diff|ids|title|comment|diffsize|rel|size|timestamp|user",
        "slots": "main",
        "difftype": "unified",
        "formatversion": "2",
        "utf8": "1"
    }
    response = WikiSession.post(data)
    if 'error' in response:
        print(response['error'])
        return
    compare = response['compare']
    if 'bodies' not in compare:
        print('No bodies found')
        return
    bodies = compare['bodies']
    if 'main' not in bodies:
        print('No main body found')
        return
    diff : str = bodies['main']
    result['diff'] = diff
    result['id'] = newer_revid
    result['parent_id'] = compare.get('fromrevid', None)
    result['comment'] = compare['tocomment']
    result['editor'] = compare['touser']
    result['timestamp'] = datetime.fromisoformat(compare['totimestamp'][:-1])
    result['is_diff'] = True
    result['title'] = compare['totitle']
    result['ns'] = compare['tons']
    return result
def _collect_compare(conn, newer_revid):
    # Check if the revision is already collected
    row = conn.execute(_SQL_FETCH_REVISION_BY_ID, {'id': newer_revid}).fetchone()
    if row is None:
        result = _calculate_diff(newer_revid)
        if result is None:
            return None
        conn.execute(_SQL_INSERT_REVISION, result)
        conn.commit()
    return newer_revid
def _collect_label(conn, rev_id, labeller, label):
    conn.execute(_SQL_INSERT_LABEL, {
        'rev_id': rev_id,
        'labeller': labeller,
        'label': label
    })
    conn.commit()
    return rev_id

def collect_sample(conn, user_id, revisions, label):
    for newer_id in revisions:
        _collect_compare(conn, newer_id)
        _collect_label(conn, newer_id, user_id, label)
def get_revisions(conn, offset=0, limit=100):
    return [row for row in conn.execute("SELECT * FROM `Revisions` ORDER BY `id` DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()]
def get_labels(conn, revisions):
    placeholder = ','.join('?'*len(revisions))

    return [dict(row) for row in conn.execute(f"SELECT * FROM `Labels` WHERE `rev_id` IN ({placeholder})", revisions).fetchall()]

    