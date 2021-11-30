from prophet import Prophet
import pandas as pd
from datetime import datetime
from datetime import timedelta
import json
from tqdm import tqdm
date_format_str = '%Y-%m-%d %H:%M:%S'

ds = [ datetime.strptime("2021-10-28 04:00:00", date_format_str) ]

n = 4

for i in range(1, 48):
  s = ds[i-1]

  next_time = s + timedelta(hours=n)
  if (next_time.strftime("%H") == "00"):
    next_time = next_time + timedelta(hours=n)

  ds.append(next_time)

for i in range(len(ds)):
  dt = ds[i]
  dt_str = dt.strftime('%Y-%m-%d %H:00:00')
  ds[i] = dt_str

with open("all_words_timeseries.json") as json_file:
  data = json.load(json_file)

emerging_word_frequencies = {}

for w in tqdm(data.keys()):
  y = data[w]
  df = pd.DataFrame(list(zip(ds, y)),
                columns =['ds', 'y'])
  m = Prophet()
  m.fit(df)

  future = m.make_future_dataframe(periods=2, freq='H')
  fcst = m.predict(future)

  diff = fcst.iloc[-1]['yhat'] - fcst.iloc[-2]['yhat']

  emerging_word_frequencies[w] = diff

  
with open("emerging_topics.json", 'w') as f:
  json.dump(emerging_word_frequencies, f)