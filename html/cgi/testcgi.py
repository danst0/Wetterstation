#!/usr/local/bin/python 
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import sys
cgitb.enable()

#print "Content-type: text/plain\n\n"
#print "testing...\n"
subprocess.Popen('/Users/danst/Documents/Archiv/Computer-Elektronik/Wetterstation/wetterstation.py', '--update')
#open('testfile', 'a').close()
print "Content-Type: text/plain;charset=utf-8"
print
print "Hello World!"


# sys.stdout('Status: 501 Not Implemented\n')
# print "Status: 404"
# print "Status:301\n\nLocation: http://www.google.com"
# cgitb.handler()
#sys.exit(0)
