import json
from statsmodels.tsa.ar_model import AutoReg
import numpy as np

if __name__=="__main__":
    fb_keywords = ['frances', 'haugen', 'whistleblower', 'facebook', 'algorithm', 'social', 'media']
    time_series_file = "time_series_format.json"

    with open(time_series_file) as json_file:
        data = json.load(json_file)
    
    word_time_series = {}

    for w in fb_keywords:
        if w in data.keys():
            word_time_series[w] = data[w]

    all_words_time_data = {}

    for w in word_time_series.keys():
        time_data = [0] * 49
        d = word_time_series[w]
        for t in d.keys():
            time_data[int(t)] = d[t]
        all_words_time_data[w] = time_data

    # x = [ i for i in range(49)]

    # print(all_words_time_data)

    # for w in all_words_time_data.keys():
    #     y = all_words_time_data[w]
    #     plt.plot(x, y, label = w)

    # plt.legend()
    # plt.show()

    word_facebook_data = all_words_time_data["facebook"]

    total = len(word_facebook_data)
    print("Total = ", total)

    train_length = 47
    train = word_facebook_data[0:train_length+1]
    # test length = 8
    test = word_facebook_data[train_length+1:]

    print("Train Data - ", train)
    print("Test Data - ", test)

    # AR example
    data = []
    for i in range(len(train)):
        if (train[i]!=0):
            data.append(np.log(train[i]))
        else:
            data.append(0)
    print("Data - ")
    print(data)
    # fit model
    model = AutoReg(data, lags=1)
    model_fit = model.fit()
    # make prediction
    yhat = []
    for i in range(8):
        y = model_fit.predict(len(data), len(data))[0]
        yhat.append(int(np.exp(y)))
        data.append((int(y)))

    # yhat = [np.exp(i) for i in yhat]
    print(yhat)
    print("Real data - ")
    print(test)

    # Train size 40
    # Test size 8
    # Train = [0, 0, 0, 0, 30, 0, 0, 0, 33, 43, 0, 0, 0, 0, 36, 36, 65, 128, 0, 
    #           72, 114, 27, 36, 36, 0, 0, 66, 25, 0, 172, 0, 0, 34, 28, 25, 321, 112, 150, 499, 1597]

    # Without making stationary
    # Predictions = [3367, 7122, 15084, 31969, 67775, 143705, 304724, 646183]
    # Real data =   [1585, 547,  131,   206,   925,   821,    495,    0]

    # After making stationary - log
    # Predictions = [106,  33,   20,    16,    15,    14,     14,     14]
    # Real data =   [1585, 547,  131,   206,   925,   821,    495,    0]
