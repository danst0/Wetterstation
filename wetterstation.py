#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Python Wetterstation

Auslesen, aggregieren, speichern und auswerten von Wetterdaten.
Aktuell können nur vordefinierte Sensoren (I2C und ELV USB-WDE1) ausgelesen werden.
Die Speicherung erfolgt in einer SQLite Datenbank, die Auswertung/Darstellung per Web-Schnittstelle.
"""
import sys
import os
# import __main__
import datetime
from pprint import pprint

import time
import random
import argparse
import D3.datenbank
import D3.diagramme
import D3.cameraremote
import D3.config

from D3.Adafruit_BMP085 import BMP085
from D3.TSL2561 import TSL2561
import pickle

class Sensors:
    """
    Klasse zum Auslesen der Sensoren über I2C und serieller Schnittstelle.
    """
    daten = {'Server': {}, 'Raum1': {}, 'Raum2': {}, u'Außen': {}}
    def __init__(self):
        pass
    
    def sensoren_auslesen(self):
        if not self.read_radio():
            print('Problem mit dem Empfänger')
            sys.exit(1)
        if not self.read_i2c():
            print('Problem mit I2C-Bus')
            sys.exit(1)

        
    def read_radio(self):
        print 'Funksensor auslesen'
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
        self.daten['Raum1']['Temperatur'] = fields[1]
        self.daten['Raum1']['Feuchtigkeit'] = fields[9]
        self.daten['Raum2']['Temperatur'] = None #float(fields[19].replace(',', '.'))
        self.daten['Raum2']['Feuchtigkeit'] = None #float(fields[21].replace(',', '.'))
        return True

    def read_i2c(self):
        print 'Lokalen I2C-Sensor auslesen'
        # Interner Sensor
#         bmp = BMP085(0x77, bus=1)

        # To specify a different operating mode, uncomment one of the following:
        # bmp = BMP085(0x77, 0)  # ULTRALOWPOWER Mode
        # bmp = BMP085(0x77, 1)  # STANDARD Mode
        # bmp = BMP085(0x77, 2)  # HIRES Mode
        server_bmp = BMP085(0x77, 3, bus=1)  # ULTRAHIRES Mode
        server_temp = 0
        for i in range(3):
            server_temp += server_bmp.readTemperature()
        server_temp = server_temp/3.0

        # Read the current barometric pressure level
        server_druck = 0
        for i in range(3):
            server_druck += server_bmp.readPressure()
        server_druck = server_druck/3.0

        # To calculate altitude based on an estimated mean sea level pressure
        # (1013.25 hPa) call the function as follows, but this won't be very accurate
        # altitude = bmp.readAltitude()

        # To specify a more accurate altitude, enter the correct mean sea level
        # pressure level.  For example, if the current pressure level is 1023.50 hPa
        # enter 102350 since we include two decimal places in the integer value
        # altitude = bmp.readAltitude(102350)

#         print "Temperature: %.2f C" % server_temp
#         print "Pressure:    %.2f hPa" % (server_druck / 100.0)
#         print server_temp
#         print server_druck / 100.0

        aussen_bmp = BMP085(0x77, 3, bus=0)  # ULTRAHIRES Mode
        aussen_temp = 0
        for i in range(3):
            aussen_temp += aussen_bmp.readTemperature()
        aussen_temp = aussen_temp/3.0

        # Read the current barometric pressure level
        aussen_druck = 0
        for i in range(3):
            aussen_druck += aussen_bmp.readPressure()
        aussen_druck = aussen_druck/3.0

#         print "Temperature: %.2f C" % temp
#         print "Pressure:    %.2f hPa" % (druck / 100.0)
#         print temp
#         print druck / 100.0


    #     print "Altitude:    %.2f" % altitude
        tsl = TSL2561()
        licht = 0
        for i in range(3):
            licht += tsl.readLux()
        licht = licht / 3.0
#         print licht
        if licht == 0:
            print 'Licht war null!'
#         licht += 1
    
    
        self.daten['Server']['Temperatur'] = server_temp
        self.daten['Server']['Luftdruck'] = server_druck / 100.0
        self.daten[u'Außen']['Temperatur'] = aussen_temp
        self.daten[u'Außen']['Luftdruck'] = aussen_druck/100.0
        self.daten[u'Außen']['Licht'] = licht
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

# def isOnlyInstance():
#     # Determine if there are more than the current instance of the application
#     # running at the current time.
#     return os.system("(( $(ps -ef | grep python | grep '[" +
#                      __main__.__file__[0] + "]" + __main__.__file__[1:] +
#                      "' | wc -l) > 1 ))") != 0

if __name__ == '__main__':
    
#     if not isOnlyInstance():
#         print 'Es kann nur eine Instanz der Wetterstation laufen.'
#         sys.exit()
    
    PARSER = argparse.ArgumentParser(description='Wetterstation')
    PARSER.add_argument('--aktualisieren', action='store_true', help='Aktualisiert die Datenbank mit den neuesten Werten')
    PARSER.add_argument('--diagramme', action='store_true', help='Generiert die Diagramme zur Anzeige auf der Webseite')
    PARSER.add_argument('--erststart', action='store_true', help='Generiert alle Diagramme neu')
    PARSER.add_argument('--kamera', action='store_true', help='Schieße ein neues Bild')
    PARSER.add_argument('--kameraIntervall', action='store_true', help='Schieße ein neues Bild, wenn die Zeit gekommen ist')

    ARGS = PARSER.parse_args()
#     print(args)
    print "Starte. Uhrzeit: " + datetime.datetime.now().strftime('%H:%M %d.%m.%Y')
# Basisobjekte
    D = D3.datenbank.Database()
    S = Sensors()
# Update Database?
    if ARGS.aktualisieren:
        S.sensoren_auslesen()
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
#     print("Beende Wetterstation")

