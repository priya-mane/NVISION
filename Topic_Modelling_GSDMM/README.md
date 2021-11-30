## Topic Modelling using GSDMM

***

Clone the repo for [GSDMM](https://github.com/rwalk/gsdmm).


1. topic_modelling.py

- Reads tweets from "delta_file.json.gz" and cluster into topics.

- Generates a file "output.json" containing clusters of words belonging to particular topic.

- Saves  cleaned tweets datewise in a file "cleaned_tweets.json" for future use.

<u>Structure of "output.json" </u>

 "date" : 

    { 
        clusters (each object is a topic containing the top 10 words (by frequency) in each cluster), 
        docs per topic, 
        most imp clusters (by #docs) 
    } 


2. fb_tweets_count.py

- Filters tweets containing words related to "Facebook Whistleblower" news and saves them in "fb_tweets.json" file.



