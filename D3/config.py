#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging


FULL_BASE_PATH = \
    '/home/danst/Wetterstation/'
sys.path.append(FULL_BASE_PATH)

ORT = 'DD AWP47'

def init_logging(text):
    logging.basicConfig(filename=FULL_BASE_PATH + 'wetter.log', format='%(asctime)s:'+text+':%(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
# logging.debug('This message should go to the log file')
# logging.info('So should this')
# logging.warning('And this, too')