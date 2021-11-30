import json
from datetime import datetime
import re
from collections import Counter
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
    if (len(words)>0 and (words[0] == "rt")):
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
    if (len(words)<3):
        return ""
    
    # merge
    text = " ".join(words)
    
    # remove space
    text = text.strip()
    
    return text

def get_tweets(file_path, freq):
    dates = set()

    tweet_file_names = []

    for line in tqdm(gzip.open(file_path)):
        doc = json.loads(line)
        dt = datetime.strptime(doc['created_at'], "%a %b %d %H:%M:%S +0000 %Y").strftime("%Y-%m-%d")
        dates.add(dt)
        break

    hour_wise_tweets = {}

    for i in range(int(24/freq)):
        hour_wise_tweets[i] = []

    for line in tqdm(gzip.open(file_path)):
        doc = json.loads(line)
        dt = datetime.strptime(doc['created_at'], "%a %b %d %H:%M:%S +0000 %Y")

        if dt.strftime("%Y-%m-%d") not in dates:
                
            file_name = "tweets_" + str(dt.strftime("%Y-%m-%d")) +".json"
            with open(file_name, 'w') as f:
                json.dump(hour_wise_tweets, f)

            tweet_file_names.append(file_name)

            for i in range(int(24/freq)):
                hour_wise_tweets[i] = []
            
            dates.add(dt.strftime("%Y-%m-%d"))

            print("Completed " + str(dt.strftime("%Y-%m-%d")))
        
        else:
            curr_hr = dt.hour
            hr_grp = int(curr_hr/freq)
            if hr_grp==int(24/freq):
                hr_grp = int(24/freq)-1

            # from extended _tweet
            if doc["truncated"]==True:
                obj = doc["extended_tweet"]
            else:
                obj = doc

            if doc["truncated"]==False:
                text = obj["text"]
            else:
                text = obj["full_text"]

            mentions = [ k["screen_name"] for k in  obj['entities']["user_mentions"] ]

            if (len(mentions)<=3):
                cleaned_text = clean_text(text, stopwords)
                if ( len(cleaned_text)>0 ):
                    hour_wise_tweets[hr_grp].append(cleaned_text)

            dates.add(dt.strftime("%Y-%m-%d"))

    return tweet_file_names

def get_word_frequencies(tweet_file, threshold):
    f = open(tweet_file,)
    data = json.load(f)


    for hr in data.keys():
        list_of_words = []
        if ( len(data[hr]) > 0 ):
            for tweet_text in data[hr]:
                list_of_words.append(tweet_text.split(" "))

            all_words = sum(list_of_words, [])
            word_frequencies = Counter(all_words)
            word_frequencies = Counter({k: c for k, c in word_frequencies.items() if c >= threshold})

            data[hr] = word_frequencies
        else:
            data[hr] = {}


    with open(tweet_file[:-5] + "_frequencies.json", 'w') as f:
        json.dump(data, f)

if __name__=="__main__":
    file_path = "delta_file.json.gz"
    stopwords = get_stopwords()
    file_names = get_tweets(file_path, 4)

    threshold = 25

    for fn in file_names:
        get_word_frequencies(fn, threshold)
    

