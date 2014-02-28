#!/usr/local/bin/python 
# -*- coding: UTF-8 -*-

# enable debugging
import subprocess
import cgitb
import sys
#from os.path import dirname

cgitb.enable()

#sys.path.append(dirname(__file__))
#sys.path.append('/Users/danst/Documents/Archiv/Computer-Elektronik/Wetterstation')

result = ''
command = ['/usr/local/bin/python2',
	'/Users/danst/Documents/Archiv/Computer-Elektronik/Wetterstation/wetterstation.py',
	'--aktualisieren',
	'--diagramme'],
	'--kameraIntervall'] #,
#	'--erststart']
try:
	result = subprocess.check_output(command, stderr=subprocess.STDOUT)
except subprocess.CalledProcessError, e:
	print "Content-Type: text/plain;charset=utf-8"
	print
	print e.output

if result != '':

	print "Content-Type: text/plain;charset=utf-8"
	print
	print '-'*10

	print result

	print '-'*10
else:
	print "Content-Type: text/plain;charset=utf-8"
	print	
	print "Status: 404"

# sys.stdout('Status: 501 Not Implemented\n')
# print "Status:301\n\nLocation: http://www.google.com"
# cgitb.handler()
#sys.exit(0)
