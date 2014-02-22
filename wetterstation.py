#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time, datetime
from pprint import pprint

import random
import argparse
import sys
import datenbank
import diagramme
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
                                

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Wetterstation')
    parser.add_argument('--update', action='store_true', help='Aktualisiert die Datenbank mit den neuesten Werten')
    parser.add_argument('--diagramme', action='store_true', help='Generiert die Diagramme zur Anzeige auf der Webseite')
    args = parser.parse_args()
#     print(args)
    print "Starte. Uhrzeit: " + str(datetime.datetime.now())
# Basisobjekte
    d = datenbank.Database()
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
        g = diagramme.Graphs(d, full_base_path)
        g.generate_graphs()
    if not args.update and not args.diagramme:
        # Wir wurden ohne Parameter aufgerufen -> CGI Modus
#         g = diagramme.Graphs()
#         g.generate_graphs()
        pass        
    print("Beende Wetterstation")
    
