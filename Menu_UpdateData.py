# email: putriintexas@hotmail.com

import tweepy
import pandas as pd
import csv
import re #regex
import string
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from datetime import date, timedelta, datetime
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory


bio = open("biodata_putri.txt", "r")
print(bio.read())
print("\n")
bio.close()

class tweets:
    pass

    def __init__(self):
        pass

    def get_api(self, consumer_key, consumer_secret, access_token, access_token_secret):
        global api
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)     
        api = tweepy.API(auth,wait_on_rate_limit=True)

        if api.verify_credentials() == False: 
            print("The user credentials are invalid.") 
        else: 
            print("The user credentials are valid.") 

    def get_kata(self, kata):
        global df
        date_since = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")
        date_until = date.today().strftime("%Y-%m-%d")
        search_word = kata
        new_search = search_word + " -filter:retweets"
        tweets = tweepy.Cursor(api.search,
        q=new_search,
        since=date_since,
        until=date_until,
        lang="id",
        result_type='recent'
        ).items(10)

        list_tweet =[]
        list_id = []
        list_username = []
        list_date = []
        for tweet in tweets:
            list_tweet.append(tweet.text)
            list_id.append(tweet.id)
            list_username.append(tweet.user.screen_name)
            list_date.append(tweet.created_at)
            df = pd.DataFrame(list(zip(list_id, list_username, list_date, list_tweet)), 
                        columns =['tweetid', 'username', 'date', 'tweets'])

     
        list_clean_tweets = []
        for each in df.tweets:
            clean_tweets = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",each).split())
            list_clean_tweets.append(clean_tweets.lower())
        #print(list_clean_tweets)
        #df['tweets_cleaned'] = list_clean_tweets

        list_clean_tweets_sastrawi = []
        for tweet in df.tweets:
            def hapus_tanda(tweet): 
                tanda_baca = set(string.punctuation)
                tweet = ''.join(ch for ch in tweet if ch not in tanda_baca)
                return tweet
            
            def hapus_katadouble(s): 
                pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
                return pattern.sub(r"\1\1", s)

            tweet=tweet.lower()
            tweet = re.sub(r'\\u\w\w\w\w', '', tweet)
            tweet=re.sub(r'http\S+','',tweet)
            # #hapus @username
            tweet=re.sub('@[^\s]+','',tweet)
            # #hapus #tagger 
            tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
            #hapus tanda baca
            tweet=hapus_tanda(tweet)
            # #hapus angka dan angka yang berada dalam string 
            tweet=re.sub(r'\w*\d\w*', '',tweet).strip()
            # #hapus repetisi karakter 
            tweet=hapus_katadouble(tweet)
            # #stemming
            factory = StemmerFactory()
            stemmer = factory.create_stemmer()
            tweet = stemmer.stem(tweet)
            list_clean_tweets_sastrawi.append(tweet)

        df['tweets_cleaned_sastrawi'] = list_clean_tweets_sastrawi
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.normalize()
        df['date'] = df['date'].astype('str')
        display(df)
        
    def to_dbsql(self):
        conn = sqlite3.connect('putriintexas.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS tweet(
      tweetid INT PRIMARY KEY,
      username VARCHAR (160),
      date DATE,
      tweets VARCHAR (160),
      tweets_cleaned_sastrawi VARCHAR (160))
      """)

        # try:
        #     df.to_sql('tweet', conn, if_exists='replace', index = False)
        # except ValueError:
        #     pass
        
        list_df = df.values.tolist()
        c.executemany("INSERT or IGNORE INTO tweet VALUES (?,?,?,?,?);", list_df)
        
        df.to_excel(r'data.xlsx', index = False)
        df.to_csv(r'data.csv', index = False)

        conn.commit()
        c.close()

tw = tweets()
tw.get_api("WHgZ7VdgxFt64JiQz0n6MGpeh", "k6WRx8qlclHgBnN0zZbEdvN9yyDwADUPRisbU7Cdw0sTCVyTHk", "1300088671719350274-fbxQxwMwFKglnVDFsai2jWDCgQqQBq", "SQ3Qftti5bG5pvnB2WbPOHzMQNa6H6iWFbU5pqM3Z9aNu")
tw.get_kata("#seventeen")
tw.to_dbsql()

        
