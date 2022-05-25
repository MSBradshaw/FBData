import pandas as pd
import pickle

df = pickle.load(open('co_covid_animation.pickle','rb'))
df.to_csv('co_covid_raw.csv', index=False)


df = pickle.load(open('poland_animation.pickle','rb'))
df.to_csv('poland_raw.csv', index=False)