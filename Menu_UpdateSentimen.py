
import pandas as pd
action.text import TfidfVectorizer
from sklearn.naive_bayes import GaussianNB
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

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
    
df['label'] = S_new
display(df)

vectorizer = TfidfVectorizer (max_features=2500)
model_g = GaussianNB()

v_data = vectorizer.fit_transform(df['tweets_cleaned_sastrawi']).toarray()

print(v_data)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(v_data, df['label'], test_size=0.2, random_state=0)
model_g.fit(X_train,y_train)

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

y_preds = model_g.predict(X_test)

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
