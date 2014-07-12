#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import serial
import pickle
from serial.tools.list_ports import comports
import D3.config
import datetime
import sys
import re
import os
import __main__

def parse_line(raw):
# #$1;1;;
# ;9,1;;;;;;;
# ;55;;;;;;;
# ;;;;;0

# $1;1;;
# ;;;;13,0;;;;
# ;;;;58;;;;
# 18,9;39;0,0;2680;0;0'
    matches = re.search(
        "^\$1;1;;" +
        8 * "([-0-9,]*);" +
        8 * "([0-9]{0,2});" +
        "([-0-9,]*);([0-9]{0,2});([-0-9,]*);([0-9]{0,4});([01]{0,1});0\r\n$", raw)
#     print matches
    if not matches:
        return None
        
    # substitute "" by None 
    values = [x if x != "" else None for x in matches.groups()]
    # first 8 values are floats per spec (temperature)
    values[0:8] = [float(x.replace(",", ".")) if x else None for x in
            values[0:8]]
    # second 8 values are ints per spec (humidity)
    values[8:16] = [int(x) if x else None for x in values[8:16]]
    # rest is float,int,float,int,bool per spec (kombi sensor)
    values[16] = float(values[16].replace(",", ".")) if values[16] else None
    values[17] = int(values[17]) if values[17] else None
    values[18] = float(values[18].replace(",",".")) if values[18] else None
    values[19] = int(values[19]) if values[19] else None
    values[20] = True if values[20] == "1" else False
    return values

def isOnlyInstance():
    # Determine if there are more than the current instance of the application
    # running at the current time.
    return os.system("(( $(ps -ef | grep python | grep '[" +
                     __main__.__file__[0] + "]" + __main__.__file__[1:] +
                     "' | wc -l) > 1 ))") != 0

if __name__ == '__main__':
    if not isOnlyInstance():
        D3.config.logging.info('Es kann nur eine Instanz von wde.py laufen.')
        sys.exit()
    com_port = '/dev/ttyUSB0'
    ports = map(lambda x: x[0], comports())
    if not com_port in ports:
        D3.config.logging.warning('Serieller Port nicht gefunden (' + com_port + ')')
        D3.config.logging.warning('Vorhandene Ports: ' + ', '.join(ports))
        sys.exit(1)
    try:
        serial = serial.Serial(com_port, baudrate=9600, timeout=180)
    except:
        D3.config.logging.error('Serielle Schnittstelle lässt sich nicht ansprechen')
        sys.exit(1)
    string = ''
    try:
        string = serial.readline()
    except:
        pass
#     string = '$1;1;;;9,1;;;;;;;;55;;;;;;;;;;;;0\r\n'
    found = False
    while True:
        val = parse_line(string)
        if val == None:
            D3.config.logging.warning('Keine Daten in den letzten', serial.timeout, 'Sekunden empfangen oder nicht korrekt')
            D3.config.logging.debug(string)
        else:
            found = True
            break
#         break
        try:
            string = serial.readline()
        except:
            D3.config.logging.warning('Keine Daten empfangen')
        
#     print string
#     print val
    if found:
#         print 'Neue Daten empfangen und gespeichert'
        pass
    val.append(datetime.datetime.now())
    pickle.dump(val, open(D3.config.FULL_BASE_PATH + 'wde.pickle', 'wb'))
    serial.close()