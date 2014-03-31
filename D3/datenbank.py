#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import time, datetime
from pprint import pprint
import random
import config
import math

class Database:
    maximum_deviation = {'Feuchtigkeit': 1.15, 'Licht': 999999.0, 'Temperatur': 1.3, 'Luftdruck': 1.2}
    file = config.FULL_BASE_PATH + 'wetter.sqlite3'
    def __init__(self):
        self.con = sqlite3.connect(self.file, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
#         self.con.text_factory = str
        self.cur = self.con.cursor()
        if not self.check_database():
            self.generate_tables()

            
    def generate_tables(self):
        self.cur.execute('CREATE TABLE weather(datum timestamp, ort text, raum text, art text, wert real)')

    def check_database(self):
        try:
            self.cur.execute('SELECT * FROM weather')
        except:
            return False
        else:
            return True
    def add_all(self, list, alle_erlauben=False):
        for first_key in list.keys():
            for sec_key in list[first_key].keys():
                self.add(first_key, sec_key, list[first_key][sec_key], alle_erlauben)
    def add(self, raum, art, wert, alle_erlauben):
        now = datetime.datetime.now()
        try:
            old_value = self.get_latest(raum, art)[4]
        except:
            old_value = wert
        
        if alle_erlauben or \
            wert == None or \
            old_value == 0 or \
            abs((wert/old_value)-1) <= self.maximum_deviation[art]:
            if wert == 0:
                print 'zero value'        
                print 'now adding', (now, config.ORT, raum, art, wert)
    #         print 'INSERT INTO weather VALUES (?, ?, ?, ?)', (now, raum, art, wert)
            self.cur.execute('INSERT INTO weather VALUES (?, ?, ?, ?, ?)', (now, config.ORT, raum, art, wert))
        else:
            print 'Wert wurde nicht in die Datenbank eingetragen, da die Abweichung zum letzten Wert zu groß ist.'
            print 'Raum', raum, 'Art', art, 'aktueller Wert', wert
            print 'Alter Wert', old_value
    
    def choose(self, von, bis, raum, art, ort=config.ORT, special_values=False):
        self.cur.execute('SELECT * FROM weather WHERE ort=? AND raum=? AND art=? ORDER BY datum ASC', (ort, raum, art))
        liste = filter(lambda x: x[0]<bis and x[0]>=von, self.cur.fetchall())
        # Alle None-Werte aus den Daten entfernen
        liste = filter(lambda x: x[4] != None, liste)
#         pprint(liste)
        if special_values:
            if len(liste) != 0:
                maximum_wert = max(map(lambda x: x[4], liste))
                minimum_wert = min(map(lambda x: x[4], liste))
                durchschnitt_wert = sum(map(lambda x: x[4], liste))/len(liste)
            else:
                maximum_wert = None
                minimum_wert = None
                durchschnitt_wert = None
        else:
            maximum_wert = None
            minimum_wert = None
            durchschnitt_wert = None
        return {'roh': liste, 'min': minimum_wert, 'max': maximum_wert, 'durchschnitt': durchschnitt_wert}

    def get_distinct_raum(self):
        self.cur.execute('SELECT DISTINCT raum FROM weather')
        return map(lambda x: x[0], self.cur.fetchall())

    def get_distinct_art(self):
        self.cur.execute('SELECT DISTINCT art FROM weather')
        tmp = self.cur.fetchall()
#         print tmp
        return map(lambda x: x[0], tmp)

    def commit(self):
        self.con.commit()
    
    def get_latest(self, raum, art):
        self.cur.execute('SELECT * FROM weather WHERE raum=? AND art=? ORDER by datum DESC', (raum, art))
        liste = self.cur.fetchone()
        return liste
        
    def close(self):
        self.con.commit()
        self.con.close()
