import json
from datetime import datetime
import re
import numpy as np
from gsdmm.gsdmm import MovieGroupProcess
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
    
    # remove hashtags
    text = re.sub(r'#\w+', '', text)
    
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

def get_tweets_datewise(stopwords, gzip_file):
    dates = set()
    date_wise_tweets = {}
    print("Getting tweets.......")
            
    for line in tqdm(gzip.open(gzip_file)):
        doc = json.loads(line)
        
        dt = datetime.strptime(doc['created_at'], "%a %b %d %H:%M:%S +0000 %Y").strftime("%Y-%m-%d")

        dates.add(dt)

        if (dt not in date_wise_tweets.keys()):
            date_wise_tweets[dt] = {
                'tweets' : [],
                'mentions' : [],
                'urls' : [],
                'hashtags' : [],
                'docs' : [],
                'clusters' : [],
                'users' : []
                }
            
        
        # from extended _tweet
        if doc["truncated"]==True:
            obj = doc["extended_tweet"]
        else:
            obj = doc
        # entities - hashtags
        hashtags = obj["entities"]["hashtags"]
        # entities - urls(list) - url
        urls = obj["entities"]["urls"]
        # entities - user_mentions(list) - screen_name
        mentions = [ k["screen_name"] for k in  obj['entities']["user_mentions"] ]
        # full_text
        if doc["truncated"]==False:
            text = obj["text"]
            
        else:
            text = obj["full_text"]
        # user details
        u = {
            "user_id" : doc["user"]["id_str"],
            "user_name" : doc["user"]["name"],
            "user_screen_name" : doc["user"]["screen_name"],
            "user_location" : doc["user"]["location"]
            }
        
            
        dt = str(dt)
            
        if (len(mentions)<=3):
            cleaned_text = clean_text(text, stopwords)
            
            docs = cleaned_text.split(' ')
            docs = [word for word in docs if len(word)>1] 
                        
            date_wise_tweets[dt]['tweets'].append(cleaned_text)
            date_wise_tweets[dt]['mentions'].append(mentions)
            date_wise_tweets[dt]['urls'].append(urls)
            date_wise_tweets[dt]['hashtags'].append(hashtags)
            date_wise_tweets[dt]['docs'].append(docs)
            date_wise_tweets[dt]['users'].append(u)
                
    return date_wise_tweets

def filter_similar_tweets(max_similarity, date_wise_tweets):
    tweet_docs = {}
      
    for dt in date_wise_tweets.keys():
        
        docs = date_wise_tweets[dt]['docs']

        tweet_docs[dt] = docs
    
    return tweet_docs

def get_clusters(tweet_docs, date_wise_tweets):
    print("clustering......")
    topic_clusters = {}
    
    for dt in tweet_docs.keys():
        print( "********" + dt + "********")
        
        dt_docs = tweet_docs[dt]
        
        vocab = set(x for doc in dt_docs for x in doc)
        
        mgp = MovieGroupProcess(K=10, alpha=0.1, beta=0.1, n_iters=10)
        n_terms = len(vocab)
        y = mgp.fit(dt_docs, n_terms)

        doc_count = np.array(mgp.cluster_doc_count)
        
        # Topics sorted by the number of document they are allocated to
        top_index = doc_count.argsort()[-10:][::-1]

        cluster = mgp.cluster_word_distribution

        for i in range(len(cluster)):
            cluster[i] = {k: v for k, v in sorted(cluster[i].items(), key=lambda item: item[1], reverse=True)[:10]}

        topic_clusters[dt] = {
            'clusters' : cluster,
            'docs per topic' : str(doc_count),
            'most imp clusters (by #docs)' : str(top_index)
            }
        topics = [mgp.choose_best_label(d)[0] for d in dt_docs]

        date_wise_tweets[dt]['clusters'] = str(topics)

    return topic_clusters, date_wise_tweets


if __name__ == "__main__":
    gzip_tweets_file = "delta_file.json.gz"

    stopwords = get_stopwords()
    date_wise_tweets = get_tweets_datewise(stopwords, gzip_tweets_file)

    max_similarity = 0.8
    tweet_docs = filter_similar_tweets(max_similarity, date_wise_tweets)
    topic_clusters, date_wise_tweets = get_clusters(tweet_docs, date_wise_tweets)

    op_file = open("output.json", "w") 
    json.dump(topic_clusters, op_file)

    tweets_file = open("cleaned_tweets.json", "w")
    for dt in tweet_docs.keys():
        tweet_obj = date_wise_tweets[dt]
        json.dump(tweet_obj, tweets_file )
        tweets_file.write("\n")
