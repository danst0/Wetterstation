#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import time, datetime
from pprint import pprint
import random



class Database:
    file = 'weather.sqlite3'
    def __init__(self):
        self.con = sqlite3.connect(self.file, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.con.text_factory = str
        self.cur = self.con.cursor()
        if not self.check_database():
            self.generate_tables()

            
    def generate_tables(self):
        self.cur.execute('CREATE TABLE weather(datum timestamp, raum text, art text, wert real)')

    def check_database(self):
        try:
            self.cur.execute('SELECT * FROM weather')
        except:
            return False
        else:
            return True
    def add_all(self, list):
        for first_key in list.keys():
            for sec_key in list[first_key].keys():
                self.add(first_key, sec_key, list[first_key][sec_key])
    def add(self, raum, art, wert):
        now = datetime.datetime.now()
#         print 'INSERT INTO weather VALUES (?, ?, ?, ?)', (now, raum, art, wert)
        self.cur.execute('INSERT INTO weather VALUES (?, ?, ?, ?)', (now, raum, art, wert))
    
    def choose(self, von, bis, raum, art):
        self.cur.execute('SELECT * FROM weather WHERE raum=? AND art=?', (raum, art))
        liste = filter(lambda x: x[0]<bis and x[0]>=von, self.cur.fetchall())
        pprint(liste)
        if len(liste) != 0:
            maximum_wert = max(map(lambda x: x[3], liste))
            minimum_wert = min(map(lambda x: x[3], liste))
            durchschnitt_wert = sum(map(lambda x: x[3], liste))/len(liste)
        else:
            maximum_wert = None
            minimum_wert = None
            durchschnitt_wert = None
        return {'roh': liste, 'min': minimum_wert, 'max': maximum_wert, 'durchschnitt': durchschnitt_wert}


    
    def get_latest(self, raum, art):
        self.cur.execute('SELECT * FROM weather WHERE raum=? AND art=? ORDER by datum DESC', (raum, art))
        liste = self.cur.fetchone()
        return liste
        
    def close(self):
        self.con.commit()
        self.con.close()