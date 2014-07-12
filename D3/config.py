#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import pickle

FULL_BASE_PATH = \
    '/home/danst/Wetterstation/'
sys.path.append(FULL_BASE_PATH)

ORT = 'DD AWP47'

class Persistent_Data:
    data = {}
    def __init__(self):
        try:
            self.data = pickle.load(open(FULL_BASE_PATH + 'persistent_data.p', 'rb'))
        except:
            self.data = {}
#         print(self.data)
#         print(self.data)
    def set(self, id, wert):
        self.data[id] = wert
    def get(self, id, start_wert=0):
        if id not in self.data.keys():
            self.data[id] = start_wert
        return self.data[id]

        
    def close(self):
        pickle.dump(self.data, open(FULL_BASE_PATH + 'persistent_data.p', 'wb'))
def init_logging(text):
    logging.basicConfig(filename=FULL_BASE_PATH + 'wetter.log', format='%(asctime)s:'+text+':%(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
# logging.debug('This message should go to the log file')
# logging.info('So should this')
# logging.warning('And this, too')