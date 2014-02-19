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

full_base_path = '/Users/danst/Documents/Archiv/Computer-Elektronik/'



class Sensors:
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
            print 'Serial: Sollte noch gar nicht funktionieren'
        
        self.read_radio()
        self.read_i2c()
    def read_radio(self):
        #string = '$1;1;;;;;;13,0;;;;;;;;58;;;;18,9;39;0,0;2680;0;0'
        string = '$1;1;;;;;;'+self.random_temp()+';;;;;'+self.random_temp()+';;;;;;;'+self.random_temp()+';;'+self.random_temp()+';;;0'
# Check for completeness
        if string[:6] != '$1;1;;' or string[-2:] != ';0':
            return None
            # should be exception
        fields = string.split(';')
#         pprint(fields)
#         print fields[8]
        self.temperature1 = float(fields[7].replace(',','.'))
        self.humidity1 = float(fields[12].replace(',','.'))
        self.temperature2 = float(fields[19].replace(',','.'))
        self.humidity2 = float(fields[21].replace(',','.'))
        
    def read_i2c(self):
        self.temperature_server = self.random_temp()
        self.pressure_server = self.random_temp()
        self.temperature_outside = self.random_temp()
        self.pressure_outside = self.random_temp()
        self.light_outside = self.random_temp()
        
    def random_temp(self):
        return str(round(((random.random()-0.2/0.5)*0.5)*100, 2)).replace('.',',')
        
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
                    line = ' ' *4 + str(int(random.random()*30))
                elif current_section == 'Luftdruck':
                    line = ' ' *4 + str(int(random.random()*1000))
                elif current_section == 'Feuchtigkeit':
                    line = ' ' *4 + str(int(random.random()*100))
                elif current_section == 'Helligkeit':
                    line = ' ' *4 + str(int(random.random()*500))
                line += '\n'

            if line.find('Temperatur') != -1:
                current_section = 'Temperatur'
            elif line.find('Luftdruck') != -1:
                current_section = 'Luftdruck'
            elif line.find('Feuchtigkeit') != -1:  
                current_section = 'Feuchtigkeit'
            elif line.find('Helligkeit') != -1:  
                current_section = 'Helligkeit'
            
            previous_line = line  
#             print line,  
            f.write(line)
        f.close()
                                
class Graphs:
    def base_graph(self, von, bis, basename, date_format_string): 
        daten = d.choose(von, bis, 'Server', 'Temperatur')
        if daten['roh'] != []:
#             print daten
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
            fig.savefig(full_base_path + 'static/graph ' + basename + '.png')


    def last_hour(self):
        self.base_graph(datetime.datetime.now() - datetime.timedelta(hours=1), datetime.datetime.now(), 'Temperatur letzte Stunde', '%H:%M')
        
    def last_day(self):
        self.base_graph(datetime.datetime.now() - datetime.timedelta(hours=24), datetime.datetime.now(), 'Temperatur letzten 24-Stunden', '%H:%M')
        
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Wetterstation')
    parser.add_argument('--update', action='store_true', help='update database with latest data')
    parser.add_argument('--graphs', action='store_true', help='generate graphs depending on last update')
    args = parser.parse_args()
    print(args)
# Basisobjekte
    d = database.Database()
    s = Sensors()
    sys.exit()
# Update Database?
    if args.update:
        d.add('Server', 'Temperatur', random.random()*30)
        d.con.commit()
        print(d.get_latest('Server', 'Temperatur'))
        s.write_to_file()
    elif args.graphs:
# Generate Graphs
        g = Graphs()
        g.last_hour()
        g.last_day()
    else:
        # Wir wurden ohne Parameter aufgerufen -> CGI Modus
        g = Graphs()
        g.last_hour()
        g.last_day()
        
    print("Beende Wetterstation")
    
