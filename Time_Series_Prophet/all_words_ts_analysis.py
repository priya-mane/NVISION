import json

if __name__=="__main__":
    time_series_file = "time_series_format.json"

    with open(time_series_file) as json_file:
        data = json.load(json_file)
    
    word_time_series = {}

    for w in data.keys():
        word_time_series[w] = data[w]

    all_words_time_data = {}

    for w in word_time_series.keys():
        time_data = [0] * 49
        d = word_time_series[w]
        for t in d.keys():
            time_data[int(t)] = d[t]
        all_words_time_data[w] = time_data

    with open("all_words_timeseries.json", 'w') as f:
        json.dump(all_words_time_data, f)