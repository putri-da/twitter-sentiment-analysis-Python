import tweepy
import pandas as pd
import csv
import re #regex
import string
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import twitter_key as keys
from datetime import date, timedelta, datetime
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import GaussianNB
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


bio = open("biodata_putri.txt", "r")
print(bio.read())
print("\n")
bio.close()

#MAIN MENU
def mainMenu():
    print("************MAIN MENU**************")

    choice = input("""Silahkan masukkan input Anda:
                      1: Update Data
                      2: Update Nilai Sentiment
                      3: Lihat Data
                      4: Visualisasi
                      5: Keluar

                      """)

    if choice == "1" :
        update_data()
    elif choice == "2" :
        update_sentiment()
    elif choice == "3" :
        lihat_data()
    elif choice== "4" :
        visualisasi()
    elif choice=="5" :
        sys.exit
    else:
        print("Anda hanya bisa memasukkan angka 1,2,3,4, atau 5.")
        print("Mohon coba lagi")
        mainMenu()

#MENU UPDATE DATA
def update_data():
        print("Update Data")
        global api
        auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
        auth.set_access_token(keys.access_token, keys.access_token_secret)     
        api = tweepy.API(auth,wait_on_rate_limit=True)

        if api.verify_credentials() == False: 
            print("The user credentials are invalid.") 
        else: 
            print("The user credentials are valid.") 

        global df
        date_since = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_until = date.today().strftime("%Y-%m-%d")
        search_word = "#seventeen"
        new_search = search_word + " -filter:retweets"
        tweets = tweepy.Cursor(api.search,
        q=new_search,
        since=date_since,
        until=date_until,
        lang="id",
        result_type='recent'
        ).items()

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
            #hapus @username
            tweet=re.sub('@[^\s]+','',tweet)
            #hapus #tagger 
            tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
            #hapus tanda baca
            tweet=hapus_tanda(tweet)
            #hapus angka dan angka yang berada dalam string 
            tweet=re.sub(r'\w*\d\w*', '',tweet).strip()
            #hapus repetisi karakter 
            tweet=hapus_katadouble(tweet)
            #stemming
            factory = StemmerFactory()
            stemmer = factory.create_stemmer()
            tweet = stemmer.stem(tweet)
            list_clean_tweets_sastrawi.append(tweet)

        df['tweets_cleaned_sastrawi'] = list_clean_tweets_sastrawi
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.normalize()
        df['date'] = df['date'].astype('str')
        df['sentiment'] = ''
        df['label'] = ''
        display(df)
        
        conn = sqlite3.connect('putriintexas.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS tweet(
      tweetid INT PRIMARY KEY,
      username VARCHAR (160),
      date DATE,
      tweets VARCHAR (160),
      tweets_cleaned_sastrawi VARCHAR (160),
      sentiment INT,
      label INT);
      """)
        print("Table created successfully")

        # try:
        #     df.to_sql('tweet', conn, if_exists='replace', index = False)
        # except ValueError:
        #     pass
        
        list_df = df.values.tolist()
        c.executemany("INSERT or IGNORE INTO tweet VALUES (?,?,?,?,?,?,?);", list_df)
        print("Records created successfully")
        df.to_excel(r'data.xlsx', index = False)
        df.to_csv(r'data.csv', index = False)

        conn.commit()
        c.close()
        conn.close()
        anykey=input("Tekan apapun untuk kembali ke menu")
        mainMenu()

#MENU UPDATE SENTIMENT
def update_sentiment():
    print("Update Data Sentiment")
    
    df = pd.read_csv("data.csv")
    display(df)
    word_token = df['tweets_cleaned_sastrawi'].tolist()
    print(word_token)

    pos_list= open("./kata_positif.txt","r")
    pos_kata = pos_list.readlines()
    neg_list= open("./kata_negatif.txt","r")
    neg_kata = neg_list.readlines()

    S = []
    for item in word_token:
        count_p = 0
        count_n = 0
        for kata_pos in pos_kata:
            if kata_pos.strip() in item:
                count_p +=1
        for kata_neg in neg_kata:
            if kata_neg.strip() in item:
                count_n +=1
    # print ("positif: "+str(count_p))
    # print ("negatif: "+str(count_n))
        S.append(count_p - count_n)

    print(S)

    S_new = []
    for a in S:
        if a<0:
            a=0
        else:
            a=1
        S_new.append(a)    
    print(S_new)
    
    df['sentiment'] = S
    df['label'] = S_new
    display(df)

    vectorizer = TfidfVectorizer (max_features=2500)
    model_g = GaussianNB()

    v_data = vectorizer.fit_transform(df['tweets_cleaned_sastrawi']).toarray()

    print(v_data)

    X_train, X_test, y_train, y_test = train_test_split(v_data, df['label'], test_size=0.2, random_state=0)
    model_g.fit(X_train,y_train)

    y_preds = model_g.predict(X_test)
    y_label = model_g.predict(v_data)
    print(y_label)

    print(confusion_matrix(y_test,y_preds))
    print(classification_report(y_test,y_preds))
    print('nilai akurasinya adalah ',accuracy_score(y_test, y_preds))

    tweet = ''
    v_data = vectorizer.transform([tweet]).toarray()
    y_preds = model_g.predict(v_data)
    
    if y_preds == 1:
        print('Positif')
    else:

        print('Negatif')
  
    df['label'] = y_label
    display(df)

    # df2 = df.drop(['tweetid','username','date', 'tweets','tweets_cleaned_sastrawi'], axis=1) 
    # df2.set_index('sentiment', inplace=True)
    # display(df2)
    # df2.to_sql('tweet' , conn, if_exists='append')
    
    conn = sqlite3.connect('putriintexas.db')
    c = conn.cursor()

    try:
        df.to_sql('tweet', conn, if_exists='replace', index = False)
    except ValueError:
        pass

    conn.commit()
    c.close()
    conn.close()
    anykey=input("Tekan apapun untuk kembali ke menu")
    mainMenu()

#MENU LIHAT DATA
def lihat_data():
    print("Lihat Data")
    print("maksimal rentang 7 hari")
    since= input('mulai tanggal (format : YYYY-MM-DD)')
    until= input('sampai tanggal (format : YYYY-MM-DD)')
    
    # def dict_factory(cursor, row):
    #     d = {}
    #     for idx, col in enumerate(cursor.description):
    #         d[col[0]] = row[idx]
    #     return d
 
    conn = sqlite3.connect('putriintexas.db')
    c = conn.cursor()
    rows = c.execute("SELECT username, date, tweets_cleaned_sastrawi FROM tweet where date >= ? and date <= ?",[since,until])
    for row in rows:
        print ("Username = ", row[0])
        print ("Date = ", row[1])
        print ("Tweet = ", row[2], "\n")

    # return print(c.fetchall())
    conn.commit()
    c.close()
    conn.close()
    anykey=input("Tekan apapun untuk kembali ke menu")
    mainMenu()

#MENU VISUALISASI
def visualisasi():
    print("Visualisasi")
    print("maksimal rentang 7 hari kebelakang")
    since= input('mulai tanggal (format : YYYY-MM-DD)')
    until= input('sampai tanggal (format : YYYY-MM-DD)')

    conn = sqlite3.connect('putriintexas.db')
    c = conn.cursor()
    rows = c.execute("SELECT sentiment FROM tweet where date >= ? and date <= ?",[since,until])
    conn.commit() 
    results = c.fetchall()
    conn.close()
   
    print ("Nilai rata-rata: "+str(np.mean(results)))
    print ("Nilai median: "+str(np.median(results)))
    print ("Standar deviasi: "+str(np.std(results)))
    labels, counts = np.unique(results, return_counts=True,)
    plt.bar(labels, counts, align='center',color='hotpink')
    plt.gca().set_xticks(labels)
    plt.show()
    anykey=input("Tekan apapun untuk kembali ke menu")
    mainMenu()

mainMenu()
