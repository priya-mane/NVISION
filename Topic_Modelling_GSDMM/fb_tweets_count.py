import json
from datetime import datetime
import re
import gzip
from tqdm import tqdm
from nltk.stem import WordNetLemmatizer

def get_stopwords():
    stopwords = set()
    with open('mysql_stopwords.txt') as f:
        lines = f.readlines()

    for l in lines:
        words = l[:-1].split("\t")
        stopwords.update(words)
    return stopwords


def clean_text(text, stopwords):
    # lowercase
    text = text.lower()
    
    # remove url
    text = re.sub(r'http\S+', '', text)
    
    # remove mentions
    text = re.sub(r'@\w+', '', text)
    
    # remove \n character
    text = (text.replace('\n', ''))
    
    # remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # remove stopwords
    words = text.split(" ")
    words = [w for w in words if not w in stopwords]
    
    # remove "rt"
    if (len(words)>0 and words[0] == "rt"):
        words = words[1:]
        
    # remove 1 character words
    words = [w for w in words if len(w)>1]
    
    # remove hashtag symbol
    text = re.sub(r'#', '', text)
    
    # Lematization
    lemmatizer = WordNetLemmatizer()
    words = [ lemmatizer.lemmatize(w) for w in words ]
    
    # Remove number
    words = [ w for w in words if not w.isnumeric()]
    
    # merge
    text = " ".join(words)
    
    # remove space
    text = text.strip()
    
    return text

def save_fb_tweets(stopwords):
    print("Getting tweets.......")
            
    for line in tqdm(gzip.open("delta_file.json.gz")):
        doc = json.loads(line)
        
        dt = datetime.strptime(doc['created_at'], "%a %b %d %H:%M:%S +0000 %Y").strftime("%Y-%m-%d")

        # from extended _tweet
        if doc["truncated"]==True:
            obj = doc["extended_tweet"]
        else:
            obj = doc


        # entities - user_mentions(list) - screen_name
        mentions = [ k["screen_name"] for k in  obj['entities']["user_mentions"] ]
        # full_text
        if doc["truncated"]==False:
            text = obj["text"]
            
        else:
            text = obj["full_text"]

        if (len(mentions)<=3):
            cleaned_text = clean_text(text, stopwords)
            
            docs = cleaned_text.split(' ')
            docs = [word for word in docs if len(word)>1]

        # Frances Haugen whistleblower Facebook algorithm social media
        fb_keywords = ['frances', 'haugen', 'whistleblower', 'facebook', 'algorithm', 'social', 'media']
        fb_keywords_set = set(fb_keywords)

        docs_set = set(docs)

        tweets_file = open("fb_tweets.json", "a")

        if(fb_keywords_set & docs_set):
                json.dump(doc, tweets_file)
                tweets_file.write("\n")
 

if __name__ == "__main__":
    stopwords = get_stopwords()
    save_fb_tweets(stopwords)

    
