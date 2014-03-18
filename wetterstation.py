#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Python Wetterstation

Auslesen, aggregieren, speichern und auswerten von Wetterdaten.
Aktuell können nur vordefinierte Sensoren (I2C und ELV USB-WDE1) ausgelesen werden.
Die Speicherung erfolgt in einer SQLite Datenbank, die Auswertung/Darstellung per Web-Schnittstelle.
"""
import sys


import datetime
from pprint import pprint

import time
import random
import argparse
import D3.datenbank
import D3.diagramme
import D3.cameraremote
import D3.config

# from D3.wde1 import WDE1

import pickle

class Sensors:
    """
    Klasse zum Auslesen der Sensoren über I2C und serieller Schnittstelle.
    """
    daten = {'Server': {}, 'Raum1': {}, 'Raum2': {}, u'Außen': {}}
    def __init__(self):

        if not self.read_radio():
            print('Problem mit dem Empfänger')
            sys.exit(1)
        if not self.read_i2c():
            print('Problem mit I2C-Bus')
            sys.exit(1)

        
    def read_radio(self):
        print 'Funksensor auslesen.'
        try:
            fields = pickle.load(open(D3.config.FULL_BASE_PATH + 'wde.pickle', 'rb'))
        except:
            fields = []
#         print fiel         
        #string = '$1;1;;;;;;13,0;;;;;;;;58;;;;18,9;39;0,0;2680;0;0'
            # should be exception
#         fields = string.split(';')
#         print len(fields)
#         pprint(fields)
        self.daten['Raum1']['Temperatur'] = float(fields[4].replace(',', '.'))
        self.daten['Raum1']['Feuchtigkeit'] = float(fields[12].replace(',', '.'))
        self.daten['Raum2']['Temperatur'] = 0 #float(fields[19].replace(',', '.'))
        self.daten['Raum2']['Feuchtigkeit'] = 0 #float(fields[21].replace(',', '.'))
        return True

    def read_i2c(self):
        self.daten['Server']['Temperatur'] = self.random_temp()
        self.daten['Server']['Luftdruck'] = self.random_temp()
        self.daten[u'Außen']['Temperatur'] = self.random_temp()
        self.daten[u'Außen']['Luftdruck'] = self.random_temp()
        self.daten[u'Außen']['Licht'] = self.random_temp()
        return True

    def random_temp_str(self):
        return \
            str(round(((random.random()-0.2/0.5)*0.5)*100, 2)).replace('.', ',')
    def random_temp(self):
        return ((random.random()-0.2/0.5)*0.5)*100

    def write_to_file(self):
        filename = 'currentdata.html'
        file_handle = open(D3.config.FULL_BASE_PATH + 'html/' + filename, 'r')
        lines = file_handle.readlines()
        file_handle.close()
        file_handle = open(D3.config.FULL_BASE_PATH + 'html/' + filename, 'w')
        current_section = ''
        previous_line = ''
        first_occurence = True
        for line in lines:
#             print line,
            if previous_line.find('value_text') != -1:
                if current_section == 'Temperatur':
                    if first_occurence:
                        line = ' ' *12 + str(int(self.daten[u'Raum1'][current_section]))
                        first_occurence = False
                    else:
                        line = ' ' *12 + str(int(self.daten[u'Außen'][current_section]))
                elif current_section == 'Luftdruck':
                    line = ' ' *8 + str(int(self.daten[u'Außen'][current_section]))
                elif current_section == 'Feuchtigkeit':
                    if first_occurence:
                        line = ' ' *12 + str(int(self.daten['Raum1'][current_section]))
                        first_occurence = False
                    else:
                        line = ' ' *12 + str(int(self.daten[u'Raum2'][current_section]))
                elif current_section == 'Licht':
                    line = ' ' *8 + str(int(self.daten[u'Außen'][current_section]))
                line += '\n'
            if line.find('Temperatur') != -1:
                current_section = 'Temperatur'
                first_occurence = True
            elif line.find('Luftdruck') != -1:
                current_section = 'Luftdruck'
            elif line.find('Feuchtigkeit') != -1:
                current_section = 'Feuchtigkeit'
                first_occurence = True
            elif line.find('Helligkeit') != -1:
                current_section = 'Licht'

            previous_line = line
#             print line,
            file_handle.write(line)
        file_handle.close()

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(description='Wetterstation')
    PARSER.add_argument('--aktualisieren', action='store_true', help='Aktualisiert die Datenbank mit den neuesten Werten')
    PARSER.add_argument('--diagramme', action='store_true', help='Generiert die Diagramme zur Anzeige auf der Webseite')
    PARSER.add_argument('--erststart', action='store_true', help='Generiert alle Diagramme neu')
    PARSER.add_argument('--kamera', action='store_true', help='Schieße ein neues Bild')
    PARSER.add_argument('--kameraIntervall', action='store_true', help='Schieße ein neues Bild, wenn die Zeit gekommen ist')

    ARGS = PARSER.parse_args()
#     print(args)
    print "Starte. Uhrzeit: " + str(datetime.datetime.now())
# Basisobjekte
    D = D3.datenbank.Database()
    S = Sensors()
# Update Database?
    if ARGS.aktualisieren:
        D.add_all(S.daten)
#         d.add('Server', 'Temperatur', random.random()*30)
        D.con.commit()
#         print(d.get_latest('Server', 'Temperatur'))
        S.write_to_file()
    if ARGS.diagramme:
# Generate Graphs
        G = D3.diagramme.Graphs(D, D3.config.FULL_BASE_PATH, ARGS.erststart)
        G.generate_graphs()
        G.close()
    if not ARGS.aktualisieren and not ARGS.diagramme:
        # Wir wurden ohne Parameter aufgerufen -> CGI Modus
#         g = diagramme.Graphs()
#         g.generate_graphs()
        pass
    print("Beende Wetterstation")

