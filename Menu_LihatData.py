import sqlite3
import pandas as pd
import numpy as np
from datetime import date, timedelta



def lihat_data():
    since= input('mulai tanggal (format : YYYY-MM-DD)')
    until= input('sampai tanggal (format : YYYY-MM-DD)')
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
 
    connection = sqlite3.connect("putriintexas.db")
    connection.row_factory = dict_factory

    cursor = connection.cursor()

    cursor.execute("SELECT username, date, tweets FROM tweet where date >= ? and date <= ?",[since,until])
# fetch all or one we'll go for all.
    results = cursor.fetchall()
    print (results)
    connection.close()
    anykey=input("Tekan apapun untuk kembali ke menu")
    mainMenu()

lihat_data()
