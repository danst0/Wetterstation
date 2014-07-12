#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Python Wetterstation

Auslesen, aggregieren, speichern und auswerten von Wetterdaten.
Aktuell können nur vordefinierte Sensoren (I2C und ELV USB-WDE1) ausgelesen werden.
Die Speicherung erfolgt in einer SQLite Datenbank, die Auswertung/Darstellung per Web-Schnittstelle.
"""
import pdb
import sys
import os
import __main__
import datetime
from pprint import pprint

import time
import random
import argparse
import D3.datenbank
import D3.diagramme
from D3.cameraremote import Camera
import D3.config

from D3.Adafruit_BMP085 import BMP085
from D3.TSL2561 import TSL2561
import pickle



class Sensoren:
    """
    Klasse zum Auslesen der Sensoren über I2C und serieller Schnittstelle.
    """
    daten = {'Server': {}, 'Raum1': {}, 'Raum2': {}, u'Außen': {}}
    def __init__(self):
        pass
    
    def sensoren_auslesen(self):

        
        if not self.read_radio():
            D3.config.logging.warning('Problem mit dem Empfänger')
            sys.exit(1)
        if not self.read_i2c():
            D3.config.logging.warning('Problem mit I2C-Bus')
            sys.exit(1)


        
        
    def read_radio(self):
        D3.config.logging.info('Funksensor auslesen')
        try:
            fields = pickle.load(open(D3.config.FULL_BASE_PATH + 'wde.pickle', 'rb'))
        except:
            fields = []
#         D3.config.logging.debug(fiel)
        #string = '$1;1;;;;;;13,0;;;;;;;;58;;;;18,9;39;0,0;2680;0;0'
            # should be exception
#         fields = string.split(';')
#         D3.config.logging.debug(len(fields))
#         pprint(fields[-1])
        if len(fields) > 0 and fields[-1] > datetime.datetime.now()-datetime.timedelta(hours=1):
#             D3.config.logging('Go')
            self.daten['Raum1']['Temperatur'] = fields[1]
            self.daten['Raum1']['Feuchtigkeit'] = fields[9]
            self.daten['Raum2']['Temperatur'] = None #float(fields[19].replace(',', '.'))
            self.daten['Raum2']['Feuchtigkeit'] = None #float(fields[21].replace(',', '.'))                
            return True
        else:
            return False

    def read_i2c(self):
        D3.config.logging.info('Lokale I2C-Sensoren auslesen')
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
            time.sleep(1)            
        server_temp = server_temp/3.0

        # Read the current barometric pressure level
        server_druck = 0
        for i in range(3):
            server_druck += server_bmp.readPressure()
            time.sleep(1)            
        server_druck = server_druck/3.0/100.0

        # To calculate altitude based on an estimated mean sea level pressure
        # (1013.25 hPa) call the function as follows, but this won't be very accurate
        # altitude = bmp.readAltitude()

        # To specify a more accurate altitude, enter the correct mean sea level
        # pressure level.  For example, if the current pressure level is 1023.50 hPa
        # enter 102350 since we include two decimal places in the integer value
        # altitude = bmp.readAltitude(102350)

#         D3.config.logging.debug("Temperature: %.2f C" % server_temp)
#         D3.config.logging.debug("Pressure:    %.2f hPa" % (server_druck / 100.0))
#         D3.config.logging.debug(server_temp)
#         D3.config.logging.debug(server_druck / 100.0)

        aussen_bmp = BMP085(0x77, 3, bus=0)  # ULTRAHIRES Mode
#         D3.config.logging.debug(aussen_bmp.available())
        if aussen_bmp.available():

            aussen_temp = 0
            for i in range(3):
                aussen_temp += aussen_bmp.readTemperature()
            aussen_temp = aussen_temp/3.0

            # Read the current barometric pressure level
            aussen_druck = 0
            for i in range(3):
                aussen_druck += aussen_bmp.readPressure()
            aussen_druck = aussen_druck/3.0/100.0

#             D3.config.logging.debug("Temperature: %.2f C" % aussen_temp)
#             D3.config.logging.debug("Pressure:    %.2f hPa" % (aussen_druck / 100.0))

            tsl = TSL2561()
    #         D3.config.logging.debug(tsl.available())
            licht = 0.0
            counter = 0.0
            for i in range(5):
                tmp = tsl.readLux(gain=0) # 0 oder leer für automatisch
                if tmp != 0:
                    licht += tmp
                    counter += 1
                time.sleep(1.2)
            if counter != 0:
                licht = licht / float(counter)
#             D3.config.logging.debug(licht)
            if licht == 0:
                D3.config.logging.warning('Licht war null!')
    #         licht += 1

        else:
            aussen_temp = None
            aussen_druck = None
            licht = None   

    
        self.daten['Server']['Temperatur'] = server_temp
#         self.daten['Server']['Luftdruck'] = server_druck
        self.daten[u'Außen']['Temperatur'] = aussen_temp
        self.daten[u'Außen']['Luftdruck'] = (aussen_druck + server_druck) / 2.0
        self.daten[u'Außen']['Licht'] = licht
        

        return True

    def random_temp_str(self):
        return \
            str(round(((random.random()-0.2/0.5)*0.5)*100, 2)).replace('.', ',')
    def random_temp(self):
        return ((random.random()-0.2/0.5)*0.5)*100

    def write_to_file(self, datenbank):
        filename = 'currentdata.html'
        file_handle = open(D3.config.FULL_BASE_PATH + 'html/' + filename, 'r')
        lines = file_handle.readlines()
        file_handle.close()
        file_handle = open(D3.config.FULL_BASE_PATH + 'html/' + filename, 'w')
        current_section = ''
        previous_line = ''
        first_occurence = True
        first_special_occurence = 3
        neue_zeilen = ''
        daten_ohne_none = {}
        special_data = {}
        for raum in self.daten.keys():
            if raum not in daten_ohne_none.keys():
                daten_ohne_none[raum] = {} 
                special_data[raum] = {}
            for abschnitt in self.daten[raum].keys():
                if self.daten[raum][abschnitt] == None:
                    daten_ohne_none[raum][abschnitt] = '--' 
                else:
                    daten_ohne_none[raum][abschnitt] = str(int(self.daten[raum][abschnitt]))
                tmp = datenbank.choose(datetime.datetime.now() - datetime.timedelta(hours=24), datetime.datetime.now(), raum, abschnitt, special_values=True)             
                if abschnitt not in special_data[raum].keys():
                    special_data[raum][abschnitt] = {}
                if tmp['durchschnitt'] != None:  
#                     pdb.set_trace()
                    special_data[raum][abschnitt]['Durchschnitt'] = str(int(tmp['durchschnitt']))
                    special_data[raum][abschnitt]['Minimum'] = str(int(tmp['min']))
                    special_data[raum][abschnitt]['Maximum'] = str(int(tmp['max']))
                else:
                    special_data[raum][abschnitt]['Durchschnitt'] = '--'
                    special_data[raum][abschnitt]['Minimum'] = '--'
                    special_data[raum][abschnitt]['Maximum'] = '--'
#                 pprint(special_data)
                
#         pprint(daten_ohne_none)
#         pdb.set_trace()
        for line in lines:
#             D3.config.logging.debug(line)
            special_value = None
            if previous_line.find('durchschnitt') != -1:
                special_value = 'Durchschnitt'
            elif previous_line.find('minimum') != -1:
                special_value = 'Minimum'
            elif previous_line.find('maximum') != -1:
                special_value = 'Maximum'
            if special_value != None:
                if current_section == 'Temperatur':
                    if first_special_occurence > 0:
                        line = ' ' *12 + special_data[u'Raum1'][current_section][special_value]
                        first_special_occurence -= 1
#                         print first_special_occurence
                    else:
                        line = ' ' *12 + special_data[u'Außen'][current_section][special_value]
                elif current_section == 'Luftdruck':
                    line = ' ' *8 + special_data[u'Außen'][current_section][special_value]
                elif current_section == 'Feuchtigkeit':
                    line = ' ' *12 + special_data[u'Raum1'][current_section][special_value]
                elif current_section == 'Licht':
                    line = ' ' *8 + special_data[u'Außen'][current_section][special_value]
                line += '\n'               
#                 pdb.set_trace()

            elif previous_line.find('value_text') != -1:
                if current_section == 'Temperatur':
                    if first_occurence:
                        line = ' ' *12 + daten_ohne_none[u'Raum1'][current_section]
                        first_occurence = False
                    else:
                        line = ' ' *12 + daten_ohne_none[u'Außen'][current_section]
                elif current_section == 'Luftdruck':
                    line = ' ' *8 + daten_ohne_none[u'Außen'][current_section]
                elif current_section == 'Feuchtigkeit':
                    line = ' ' *12 + daten_ohne_none['Raum1'][current_section]
                elif current_section == 'Licht':
                    line = ' ' *8 + daten_ohne_none[u'Außen'][current_section]
                line += '\n'
            if line.find('Temperatur') != -1:
                current_section = 'Temperatur'
                first_occurence = True
#                 first_special_occurence = True
            elif line.find('Luftdruck') != -1:
                current_section = 'Luftdruck'
            elif line.find('Feuchtigkeit') != -1:
                current_section = 'Feuchtigkeit'
            elif line.find('Helligkeit') != -1:
                current_section = 'Licht'

            previous_line = line
#             print line,
            neue_zeilen = neue_zeilen + line
#         print neue_zeilen
        if neue_zeilen != '':
            file_handle.write(neue_zeilen)
        file_handle.close()

def isOnlyInstance():
    # Determine if there are more than the current instance of the application
    # running at the current time.
    return os.system("(( $(ps -ef | grep python | grep '[" +
                     __main__.__file__[0] + "]" + __main__.__file__[1:] +
                     "' | wc -l) > 1 ))") != 0

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(description='Wetterstation')
    PARSER.add_argument('--aktualisieren', action='store_true', help='Aktualisiert die Datenbank mit den neuesten Werten')
    PARSER.add_argument('--alleerlauben', action='store_true', help='Erlaube alles Werte, ohne auf interne Grenzen zu achten')
    PARSER.add_argument('--diagramme', action='store_true', help='Generiert die Diagramme zur Anzeige auf der Webseite')
    PARSER.add_argument('--erststart', action='store_true', help='Generiert alle Diagramme neu')
    PARSER.add_argument('--kamera', action='store_true', help='Schieße ein neues Bild')
    PARSER.add_argument('--kameraIntervall', action='store_true', help='Schieße ein neues Bild, wenn die Zeit gekommen ist')

    ARGS = PARSER.parse_args()
#     print(args)
    text = ''
    if ARGS.aktualisieren:
        text += 'AKT'
    if ARGS.diagramme:
        text += 'DIA'
    if ARGS.kamera:
        text += 'CAM'
    D3.config.init_logging(text)
    D3.config.logging.info("Starte. Uhrzeit: " + datetime.datetime.now().strftime('%H:%M %d.%m.%Y'))
#     D3.config.logging.info('Befehlszeile; aktualisieren: {}, diagramme: {}, kamera: {}'.format(ARGS.aktualisieren, ARGS.diagramme, ARGS.kamera))
    if ARGS.kamera:
        D3.config.logging.info('Aufnahme Kamerabild')
        c = Camera()
        if c.take_picture():
            D3.config.logging.info('Kamerabild herunterladen')        
            c.download_picture()
        else:
            c.alternative_picture()
    if not isOnlyInstance():
        D3.config.logging.warn('Es kann nur eine Instanz der Wetterstation laufen.')
        sys.exit(1)

# Basisobjekte
    D = D3.datenbank.Database()
    S = Sensoren()
# Update Database?
    if ARGS.aktualisieren:
        S.sensoren_auslesen()
        D.add_all(S.daten, ARGS.alleerlauben)
#         d.add('Server', 'Temperatur', random.random()*30)
        D.commit()
#         print(d.get_latest('Server', 'Temperatur'))
        S.write_to_file(D)

    if ARGS.diagramme:
# Generate Graphs
        G = D3.diagramme.Graphs(D, D3.config.FULL_BASE_PATH, ARGS.erststart)
        G.generate_graphs()
        G.close()
#     print("Beende Wetterstation")
    D.close()
