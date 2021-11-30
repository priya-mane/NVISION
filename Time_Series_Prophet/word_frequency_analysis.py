import json
if __name__=="__main__":
    file_names = ["tweets_2021-09-29_frequencies.json", "tweets_2021-09-30_frequencies.json",
                    "tweets_2021-10-01_frequencies.json", "tweets_2021-10-02_frequencies.json",
                    "tweets_2021-10-03_frequencies.json", "tweets_2021-10-04_frequencies.json",
                    "tweets_2021-10-05_frequencies.json", "tweets_2021-10-06_frequencies.json"
                    ]
    date_wise_data = []
    for fn in file_names:
        with open(fn) as json_file:
            data = json.load(json_file)
            date_wise_data.append(data)

    all_words = set()

    for data in date_wise_data:
        for k in data.keys():
            time_frame_words = data[k].keys()
            all_words.update(time_frame_words)

    print("We have ", len(all_words), " unique words!")
    # 6399 unique words

    word_series = {}
    for word in all_words:
        word_series[word] = {}

    freq_sampling = 4
    samples_per_day = int(24/freq_sampling)
    day = 0

    for data in date_wise_data:
        for time_stamps in data.keys():
            words_for_the_time = data[time_stamps]
            for w in words_for_the_time.keys():
                key = str(int(int(time_stamps) + int(samples_per_day)*int(day)))
                if time_stamps*samples_per_day*day in word_series[w]:
                    word_series[w][key] += data[time_stamps][w]
                else:
                    word_series[w][key] = data[time_stamps][w]
        day += 1

    

    with open("time_series_format.json", 'w') as f:
        json.dump(word_series, f)


