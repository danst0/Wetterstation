# -*- coding: utf-8 -*-

# Copyright (C) 2011 by Researchstudio iSpace
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re
import serial
import threading
import time

class FormatError(BaseException):

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return ("FormatError: {0}".format(self._msg))


class Event(object):
    """Event represents a notification event that holds all relevant information
    of a sensor update.

    Attributes:
        - adr:          The address of the sensor represented as integer.
                        Ranging from 0 to 7 if sensor is not a kombi sensor, 8
                        otherwise.
        - timestamp:    The Unix timestamp of the measurement.
        - kombi:        True if this sensor represents a kombi sensor, False
                        otherwise.
        - changed:      True if anything changed regarding the last state of the
                        sensor.
        - event_type:   The type of the event. Represents one of WDE1.SENSOR_*.
        - temperature:  The current temperature of the wheather sensor.
        - humidity:     The current humidity of the wheather sensor.
        - windspeed:    The current windspeed if the event represents a kombi
                        sensor.
        - raincycles:   The current raincycles if the event represents a kombi
                        sensor.
        - rain:         True if the sensor is a kombi one and it is raining,
                        False otherwise.
    """
    pass


class _Sensor(object):

    def __init__(self, adr, kombi=False):
        self._values = None

        if not kombi:
            self._values = {
                "temperature": None,
                "humidity": None,
            }
        else:
            self._values = {
                "temperature": None,
                "humidity": None,
                "windspeed": None,
                "raincycles": None,
                "rain": None
            }
        self._kombi = kombi
        self._adr = adr
        self._changed = False
        self._timestamp = int(time.time())
        self._event_type = WDE1.SENSOR_UNREACHABLE

    def __setattr__(self, key, value):
        if key not in ["temperature", "humidity", "windspeed", "raincycles",
                "rain"]:
            object.__setattr__(self, key, value)
        else:
            if self._values[key] == None and value != None:
                self._event_type = WDE1.SENSOR_AVAILABLE
            if self._values[key] != None and value == None:
                self._event_type = WDE1.SENSOR_UNREACHABLE
            if self._values[key] != None and value != None:
                self._event_type = WDE1.SENSOR_UPDATE
            self._timestamp = int(time.time())
            if self._values[key] != value:
                self._changed = True
            self._values[key] = value

    def get_event(self):
        e = Event()
        for key in self._values:
            setattr(e, key, self._values[key])
        e.timestamp = self._timestamp
        e.adr = self._adr
        e.changed = self._changed
        e.event_type = self._event_type
        e.kombi = self._kombi
        self._changed = False
        return e


class WDE1(threading.Thread):

    ADR_KOMBI = 8

    SENSOR_AVAILABLE = "SENSOR_AVAILABLE"
    SENSOR_UPDATE = "SENSOR_UPDATE"
    SENSOR_UNREACHABLE = "SENSOR_UNREACHABLE"

    NOTIFY_CHANGE = 1
    NOTIFY_ALL = 2

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.daemon = True
        self._observers = []
        self._observers_all = []

        self._sensors2 = [_Sensor(i) for i in range(8)]
        self._sensors2.append(_Sensor(8, kombi=True))
        self._version = None
        self.ser = serial.Serial(port)

    def add_observer(self, fn, adr=None, notify=NOTIFY_CHANGE):
        if notify == WDE1.NOTIFY_CHANGE:
            if not (fn,adr) in self._observers:
                self._observers.append((fn,adr))
        else:
            if not (fn,adr) in self._observers_all:
                self._observers_all.append((fn,adr))

    @property
    def observers_change(self):
        return self._observers

    @property
    def observers_all(self):
        return self._observers_all

    @property
    def version(self):
        if not self._version:
            self._version = self._get_version()
        return self._version

    def _get_version(self):
        if not self.ser.isOpen():
            self.ser.open()
        self.ser.flushInput
        self.ser.flushOutput()
        self.ser.write("?")
        self.ser.readline() # empty line
        line2 = self.ser.readline()
        self.ser.readline() # baud rate
        #TODO: error handling
        matches = re.match("^ELV USB-WDE1 v([0-9.]+)", line2)
        return matches.group(1)

    def _parse_line(self, raw):
        matches = re.search(
            "^\$1;1;;" +
            8 * "([-0-9,]*);" +
            8 * "([0-9]{0,2});" +
            "([-0-9,]*);([0-9]{0,2});([0-9]{0,3},?[0-9]?);([0-9]{0,4});([01]);0\r\n$", raw
        )
        if not matches:
            # currently only OpenLog format is supported
            # TODO: should switch format here
            raise FormatError("currently only OpenLog format is supported")

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

    def _update_state(self, values):
        for i in range(0, 8):
            self._sensors2[i].temperature = values[i]
            self._sensors2[i].humidity = values[i+8]
        self._sensors2[WDE1.ADR_KOMBI].temperature = values[16]
        self._sensors2[WDE1.ADR_KOMBI].humidity = values[17]
        self._sensors2[WDE1.ADR_KOMBI].windspeed = values[18]
        self._sensors2[WDE1.ADR_KOMBI].raincycles = values[19]
        self._sensors2[WDE1.ADR_KOMBI].rain = values[20]

    def _notify(self):
        for key in range(0, 9):
            e = self._sensors2[key].get_event()
            if e.changed:
                for (obs,adr) in self._observers:
                    if adr == None or adr == key:
                        t= threading.Thread(target=obs,
                                args=(self,e))
                        t.start()
            for (obs,adr) in self._observers_all:
                if adr == None or adr == key:
                    t= threading.Thread(target=obs,
                            args=(self,e))
                    t.start()

    def start_reading(self,blocking=True):
        self._run = True
        if blocking:
            self._do_run()
        else:
            self.start()

    def _do_run(self):
        if not self.ser.isOpen():
            self.ser.open()
        line = self.ser.readline()
        while self._run:
            values = self._parse_line(line)
            self._update_state(values)
            self._notify()
            line = self.ser.readline()

    def run(self):
        self._do_run()

    def close(self):
        self._run = False
        self.ser.close()