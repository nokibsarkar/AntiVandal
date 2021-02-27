SPECIAL_WORDS = [] # the list of special words to be checked
SPECIAL_WORD_COUNT = len(SPECIAL_WORDS)
SPECIAL_TAGS = [
    # tuples will be checked as logical or expression
    'mw-rollback',
    ('mw-undo', 'mw-manual-revert'),
    'আলাপ পাতা খালি করা হয়েছে!',
    ('mw-new-redirect', 'mw-changed-changed-target'),
    'অন্য ব্যবহারকারীর পাতা তৈরি',
    'অত্যন্ত সংক্ষিপ্ত নতুন নিবন্ধ',
    'visualeditor',
    'visualeditor-wikitext',
    'mw-removed-redirect-target',
    'ব্যবহারকারী আত্মজীবনী তৈরি করেছেন',
    'বাংলা নয় এমন বিষয়বস্তু অতি মাত্রায় যোগ',
    'mw-replace',
    ('mw-blank' , 'blanking'),
    'নতুন ব্যবহারকারী বহিঃসংযোগ যুক্ত করেছেন',
    ####--নতুন ব্যবহারকারী দ্রুত অপসারণ ট্যাগ বাতিল করেছেন
    'নতুন ব্যবহারকারী দ্রুত অপসারণ ট্যাগ বাতিল করেছেন',
    ('নতুন ব্যবহারকারী পাতা খালি করেছেন!', 'mw-manual-revert'),
     'আলাপ পাতা খালি করা হয়েছে!',
    'emoji' 'mw-changed-changed-target',
    'অনুচ্ছেদ খালি করা হয়েছে',
    'তথ্য অপসারণ',
    'চিত্রের বিবরণ বাংলা নয়',
    'অস্বাভাবিক পুনর্নির্দেশ'
] 
SPECIAL_TAG_COUNT = len(SPECIAL_TAGS)
REGEXP_CLASS = re.compile("only for getting the class").__class__ # the class for confirming if an element is actually a regexp or not

NAMESPACE_MAPPER = {
    0 : 0, #(প্রধান/নিবন্ধ) 
    1 : 1, #আলাপ 	১
    2 : 2, #২ ব্যবহারকারী
    3 : 3, #ব্যবহারকারী আলাপ 	৩
    4 : 4, #৪ উইকিপিডিয়া
    5 : 5, #উইকিপিডিয়া আলোচনা 	৫
    6 : 6, #৬ 	চিত্র 
    7 : 7, #চিত্র আলোচনা 	৭
    8 : 8, #৮ 	মিডিয়াউইকি 
    9 : 9, #িডিয়াউইকি আলোচনা৯
    10 : 10, #১০ টেমপ্লেট 
    11 : 11, #টেমপ্লেট আলোচনা১১
    12 : 12, #১২ 	সাহায্য 
    13 : 13, #সাহায্য আলোচনা 	১৩
    14 : 14, #১৪ 	বিষয়শ্রেণী 
    15 : 15, #বিষয়শ্রেণী আলোচনা 	১৫
    100 : 16, #১০০ 	প্রবেশদ্বার 
    101 : 17, #প্রবেশদ্বার আলোচনা 	১০১
    828: 18, #৮২৮ 	মডিউল 
    829 : 19, #মডিউল আলাপ 	৮২৯
    2300 : 20, #২৩০০ 	গ্যাজেট 
    2301 : 21, #গ্যাজেট আলোচনা 	২৩০১
    2302 : 22, #২৩০২ 	গ্যাজেট সংজ্ঞা
    2303 : 23 #গ্যাজেট সংজ্ঞার আলোচনা 	২৩০৩
}
NAMESPACE_COUNT = len(NAMESPACE_MAPPER) #total number of namespace
ILLEGAL_USERNAME = None #the regexp pattern for illegal username
CACHE_NAME = "cache.db" #sqlite3 database for cache
CACHE_INIT = r"""CREATE TABLE  IF NOT EXISTS Contents (
    PageID INT PRIMARY_KEY,
    User TEXT DEFAULT NULL,
    Content TEXT DEFAULT NULL,
    RevID INT DEFAULT 0,
    Pointer INT DEFAULT 0
    ) ;""" # initialization of cache database
SIZE_DENOMINATOR = 1e3 #the denominator which will be used for converting from raw diff size
URL_PATTERN = re.compile("(?:https?://\S+)", re.U | re.I) # it will identify links
EMAIL_PATTERN = re.compile("[^@]{4,}@[^\.]+\.\S{3,}")
PHONE_PATTERN = re.compile("(?:\(?\+? *880 *\)?)?[\d\-\,]{10,}") # phone number identifier
FEATURE_COUNT = (
    1 # bias value
    + NAMESPACE_COUNT
    + SPECIAL_TAG_COUNT # in the previous revision
    + SPECIAL_TAG_COUNT # in the changed revision
    + SPECIAL_WORD_COUNT ## in the previous revision
    + SPECIAL_WORD_COUNT # in the previous revision
    + 1 + 1 # for url count in both revision
    + 1 + 1 # for email count in both revision
    + 1 + 1 # for phone count in both revision
    + 1 # for byte differnece of revision
    + 1  # for seconds differnece between two consecutive edit
    + 1   ## tla = total link added
    + 1    ## tlr = total link removed
     + 1   ## tea = total external link added
     + 1   ## ter = total external link removed
     + 1   ## tea/tla
     + 1   ## ter/tlr
     + 1   ## trl = total removed line
     + 1   ## tal = total added line
     + 1   ## twr = total word removed
     + 1   ## twa = total word added
    + 1 # for revision id difference
    + 1 # if the title contains '/' literal i.e in the subpage
    + 1 # whether previous edit was made by me
    + 1 # for whether the editor is from IP
    # if from IP then all of the below will be zero
    + 1 # for similarity between title and username
    + 1 # for similary between username and comment
    + 1  # for illegal word count in username
)
OUTPUT_ROLLBACK = 0 #rollback the edit
OUTPUT_NOTIFY = 1 # notify the user
OUTPUT_OFFENSIVE = 2 # the edit was an offensive
OUTPUT_COUNT = 3
FETCH_REQUEST_PARAMS = [
    ("action", "query"),
    ("format", "json")
]
FEATURE_COUNT
