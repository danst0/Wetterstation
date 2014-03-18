#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import serial
import pickle
from serial.tools.list_ports import comports
import D3.config
import datetime

if __name__ == '__main__':
    com_port = '/dev/ttyUSB0'
    ports = map(lambda x: x[0], comports())
    if not com_port in ports:
        print('Serieller Port nicht gefunden (' + com_port + ')')
        print('Vorhandene Ports: ' + ', '.join(ports))
        sys.exit(1)
    try:
        serial = serial.Serial(com_port, baudrate=9600, timeout=240)

    except:
        print 'Serielle Schnittstelle lässt sich nicht ansprechen'
        sys.exit(1)
    string = serial.readline()
    print string
    fields = string.split(';')
    if fields[0] == '$1' and fields[1] == '1' and fields[-1] == '0\r\n' and len(fields) == 25:
        for f in range(len(fields)):
            if fields[f] == '':
                fields[f] = None

        fields.append(datetime.datetime.now())
        pickle.dump(fields, open(D3.config.FULL_BASE_PATH + 'wde.pickle', 'wb'))