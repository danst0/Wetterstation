#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sqlite3
import time, datetime
from pprint import pprint

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import random
import argparse
import sys
import database
import camera_remote
import serial
from serial.tools.list_ports import *
import cgitb
# cgitb.enable()
# import pylab

full_base_path = '/Users/danst/Documents/Archiv/Computer-Elektronik/Wetterstation/'



class Sensors:
    daten={'Server': {}, 'Raum1': {}, 'Raum2': {}, u'Außen': {}}
    def __init__(self):
        self.com_port = '/dev/tty.Bluetooth-Modem'
        ports = map(lambda x: x[0], comports())
        if not self.com_port in ports:
            print('Serieller Port nicht gefunden (' + self.com_port + ')')
            print('Vorhandene Ports: ' + ', '.join(ports))
            sys.exit(1)
        try:
            self.serial = serial.Serial(self.com_port, 115200)
            self.serial.close()
        except:
            print 'Serial: Alles ok, sollte noch gar nicht funktionieren'
        
        if not self.read_radio():
            print('Problem mit dem Empfänger')
            sys.exit(1)
        if not self.read_i2c():
            print('Problem mit I2C-Bus')
            sys.exit(1)
#         pprint(self.daten)
    
    def read_radio(self):
        #string = '$1;1;;;;;;13,0;;;;;;;;58;;;;18,9;39;0,0;2680;0;0'
        string = '$1;1;;;;;;'+self.random_temp_str()+';;;;;'+self.random_temp_str()+';;;;;;;'+self.random_temp_str()+';;'+self.random_temp_str()+';;;0'
# Check for completeness
        if string[:6] != '$1;1;;' or string[-2:] != ';0':
            return False
            # should be exception
        fields = string.split(';')
#         pprint(fields)
#         print fields[8]
        self.daten['Raum1']['Temperatur'] = float(fields[7].replace(',','.'))
        self.daten['Raum1']['Feuchtigkeit'] = float(fields[12].replace(',','.'))
        self.daten['Raum2']['Temperatur']  = float(fields[19].replace(',','.'))
        self.daten['Raum2']['Feuchtigkeit'] = float(fields[21].replace(',','.'))
        return True
        
    def read_i2c(self):
        self.daten['Server']['Temperatur'] = self.random_temp()
        self.daten['Server']['Luftdruck'] = self.random_temp()
        self.daten[u'Außen']['Temperatur'] = self.random_temp()
        self.daten[u'Außen']['Luftdruck'] = self.random_temp()
        self.daten[u'Außen']['Licht'] = self.random_temp()
        return True
        
    def random_temp_str(self):
        return str(round(((random.random()-0.2/0.5)*0.5)*100, 2)).replace('.',',')
    def random_temp(self):
        return ((random.random()-0.2/0.5)*0.5)*100
        
    def write_to_file(self):
        filename = 'currentdata.html'
        f = open(full_base_path + 'html/' + filename, 'r')
        lines = f.readlines()
        f.close()
        f = open(full_base_path + 'html/' + filename, 'w')
        current_section = ''
        previous_line =''
        for line in lines:
#             print line,
            if previous_line.find('value_text') != -1:
                if current_section == 'Temperatur':
                    line = ' ' *4 + str(int(self.daten[u'Außen'][current_section]))
                elif current_section == 'Luftdruck':
                    line = ' ' *4 + str(int(self.daten[u'Außen'][current_section]))
                elif current_section == 'Feuchtigkeit':
                    line = ' ' *4 + str(int(self.daten['Raum1'][current_section]))
                elif current_section == 'Licht':
                    line = ' ' *4 + str(int(self.daten[u'Außen'][current_section]))
                line += '\n'
            if line.find('Temperatur') != -1:
                current_section = 'Temperatur'
            elif line.find('Luftdruck') != -1:
                current_section = 'Luftdruck'
            elif line.find('Feuchtigkeit') != -1:  
                current_section = 'Feuchtigkeit'
            elif line.find('Helligkeit') != -1:  
                current_section = 'Licht'
            
            previous_line = line  
#             print line,  
            f.write(line)
        f.close()
                                
class Graphs:
    font = {
        'family' : 'sans-serif',
        'weight' : 'ultralight',
        'size'   : 9}

    def aggregate_data(self, datum, inhalt, von, bis):
        zeitspanne = bis - von
        abstand = zeitspanne/200
        print abstand

        return datum, inhalt

    def aggregate_graph(self, von, bis, raeume, arten, basename, date_format_string, groesse=(8,4), hd=False): 
        if hd:
            details=800
            basename = basename + '_hd'
            self.font['size'] = 5
        else:
            details=200
            self.font['size'] = 9
        matplotlib.rc('font', **self.font)
        fig = plt.figure(figsize=groesse, dpi=details)
        ax = fig.add_subplot(111)
        # War mal '%Y-%m-%d %H:%M:%S'
        xfmt = md.DateFormatter(date_format_string)
        ax.xaxis.set_major_formatter(xfmt)
        fig.autofmt_xdate()
        plt.xlabel('Datum/Uhrzeit')
        plt.grid(True)

        for raum in raeume:
            for art in arten:  
                plt.ylabel(art)
                daten = d.choose(von, bis, raum, art)
                list_of_datetimes = map(lambda x: x[0], daten['roh'])
                datum = matplotlib.dates.date2num(list_of_datetimes)   
                inhalt = map(lambda x: x[3], daten['roh'])
                datum, inhalt = self.aggregate_data(datum, inhalt, von, bis)
                if inhalt != []:
                    plt.plot(datum, inhalt, label=raum, marker='.')
        if hd:
            plt.legend(loc='best')
            fig.suptitle(u'Verlauf zwischen ' + str(von) + ' und ' + str(bis), fontsize=8)
#             plt.figtext(0.5,0.05,(u'Verlauf zwischen ' + str(von) + ' und ' + str(bis)), fontsize=10, ha='center')            
        else:
            plt.legend(loc='upper left')
        plt.show()
#         pfad = full_base_path + 'html/diagramme/' + ''.join(raeume) + '_' + ''.join(arten) + '_' + basename + '.png'
        pfad = full_base_path + 'html/diagramme/' + u'Räume' + '_' + ''.join(arten) + '_' + basename + '.png'
#         print pfad
        fig.savefig(pfad)
        plt.close()
        
    def base_graph(self, von, bis, raum, art, basename, date_format_string):
        self.font['size'] = 9
        matplotlib.rc('font', **self.font)
        daten = d.choose(von, bis, raum, art)
        if daten['roh'] != []:
#             pprint(daten)
            list_of_datetimes = map(lambda x: x[0], daten['roh'])
            datum = matplotlib.dates.date2num(list_of_datetimes)
        
            inhalt = map(lambda x: x[3], daten['roh'])

            fig = plt.figure()
            ax = fig.add_subplot(111)
            # War mal '%Y-%m-%d %H:%M:%S'
            xfmt = md.DateFormatter(date_format_string)
            ax.xaxis.set_major_formatter(xfmt)
            fig.autofmt_xdate()
            ax.plot(datum, inhalt)
            plt.show()
#             print 'Speichere: ' + 'html/diagramme/' + raum + '_' + art + '_' + basename + '.png'
#             fig.savefig(full_base_path + 'html/diagramme/' + raum + '_' + art + '_' + basename + '.png')
            plt.close()

    def generate_graphs(self):
#         print d.get_distinct_art()
        print 'Generiere Diagramme'
        for art in d.get_distinct_art():
            print art
            for raum in d.get_distinct_raum():
                self.base_graph(datetime.datetime.now() - datetime.timedelta(hours=1), datetime.datetime.now(), raum, art, '1 Stunde', '%H:%M')     
                self.base_graph(datetime.datetime.now() - datetime.timedelta(hours=24), datetime.datetime.now(), raum, art, '24 Stunden', '%H:%M')
            size = (7,2)
            if art in ['Licht', 'Feuchtigkeit']:
                size = (3,2)
            for details in [False, True]:
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(hours=1), datetime.datetime.now(), d.get_distinct_raum(), (art,), '1 Stunde', '%H:%M', groesse=size, hd=details)
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(hours=24), datetime.datetime.now(), d.get_distinct_raum(), (art,), '24 Stunden', '%H:%M', groesse=size, hd=details)
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(days=7), datetime.datetime.now(), d.get_distinct_raum(), (art,), '7 Tage', '%Y-%m-%d', groesse=size, hd=details)
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now(), d.get_distinct_raum(), (art,), '30 Tage', '%Y-%m-%d', groesse=size, hd=details)
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now(), d.get_distinct_raum(), (art,), '1 Quartal', '%Y-%m-%d', groesse=size, hd=details)
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now(), d.get_distinct_raum(), (art,), '1 Jahr', '%Y-%m-%d', groesse=size, hd=details)
                self.aggregate_graph(datetime.datetime.now() - datetime.timedelta(days=11365), datetime.datetime.now(), d.get_distinct_raum(), (art,), 'Alles', '%Y-%m-%d', groesse=size, hd=details)
            
        
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Wetterstation')
    parser.add_argument('--update', action='store_true', help='Aktualisiert die Datenbank mit den neuesten Werten')
    parser.add_argument('--diagramme', action='store_true', help='Generiert die Diagramme zur Anzeige auf der Webseite')
    args = parser.parse_args()
    print(args)
# Basisobjekte
    d = database.Database()
    s = Sensors()
# Update Database?
    if args.update:
        d.add_all(s.daten)
#         d.add('Server', 'Temperatur', random.random()*30)
        d.con.commit()
#         print(d.get_latest('Server', 'Temperatur'))
        s.write_to_file()
    if args.diagramme:
# Generate Graphs
        g = Graphs()
        g.generate_graphs()
    if not args.update and not args.diagramme:
        # Wir wurden ohne Parameter aufgerufen -> CGI Modus
        g = Graphs()
        g.generate_graphs()
        
    print("Beende Wetterstation")
    
