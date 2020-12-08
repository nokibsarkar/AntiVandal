import pickle
import pywikibot as pb
import json
contrib_list = 'User:Nokib Sarkar/Antivandal/list.json'
contrib_page = 'User:%s/ধ্বংসরোধ উপাত্ত'
positive = 'positive.data'
negative = 'negative.data'
bn = pb.Site('bn', 'wikipedia')
contributors = json.loads(pb.Page(bn,contrib_list).text)
with open('X.data', 'rb') as fp:
    X = pickle.load(fp)
Conflicts = set()
def extract(lines):
    global X, Conflicts
    count = 0
    label = 0
    for line in lines:
        for i in line.split(','):
            if i in X:
                if X[i] != label:  # conflicts
                    del X[i]
                    Conflicts.add(i)
            else:
                X[i] = label
                count += 1
        label = label ^ 1
    return count
for username in contributors:
    pg = pb.Page(bn, contrib_page % username)
    if(pg.text == ''):
        continue
    count  = extract(pg.text.split('\n'))
    pg.text = ''
    pg.save('বট কর্তৃক অবদানকারী হতে উপাত্ত %dটি নমুনা সংগ্রহ করা হয়েছে ([[ব্যবহারকারী:Nokib Sarkar/ধ্বংসরোধ|বিস্তারিত]])' % count)
pg = pb.Page(bn,'User:Nokib Sarkar/ধ্বংসরোধ/দ্বন্দ্ব')
pg.text = '%s\n*%s' % (
    pg.text,
    '\n*'.join(Conflicts)
)
if(len(Conflicts)):
    pg.save('বট কর্তৃক %dটি নমুনা দ্বন্দ্ব সংগ্রহ করা হয়েছে ([[ব্যবহারকারী:Nokib Sarkar/ধ্বংসরোধ|বিস্তারিত]])' % len(Conflicts))
with open('X.data', 'wb') as fp:
    X = pickle.dump(X, fp)
    print('Successfully Saved')
