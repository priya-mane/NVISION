## Time Series Analysis Approach - Prophet

***

1. get_word_frequencies.py

- Samples the tweets per 4 hour interval and saves in "tweets_< date >.json"

- Calculates frequency for each word and saves it in file "tweets_< date >_frequencies.json".

2. word_frequency_analysis.py

- For each word, creates a json object with its time interval and frequency of that word in the particular time interval. Saves the results to "time_series_format.json"

3. all_words_ts_analysis.py

- Creates a time series for each word, adds 0 for all intervals where the word did not appear and saves it in "all_words_timeseries.json" file.

4. time_series_words_fb.py

- Autoregressive model for word frequencies related to Facebook News.

5. Analysis_using_prophet.py

- Read word frequencies from "all_words_timeseries.json", forecasts the frequency for next interval for each word and saves the difference in file "emerging_topics.json"
