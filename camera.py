#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import argparse

local_path = '/root/'
raspistill = 'raspistill'
convert = 'convert'
class Camera:
    def __init__(self):
        pass
    def take_picture(self):
        print 'Schieße Foto'
        image_raw = local_path+'webcamraw.jpg'
        image = local_path+'webcam.jpg'
        command = [raspistill, image_raw, '-t 0']
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        command = [convert, image_raw, '-pointsize 72', '-fill white', '-gravity SouthWest', "-annotate +50+100 'D3 Wetterstation %[exif:DateTimeOriginal]'", image]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        print "Foto erstellt"
        
if __name__ == "__main__":
    c = Camera()
    parser = argparse.ArgumentParser(description='Kamera')
    parser.add_argument('--fullpanorama', action='store_true', help='Aufnahme eines vollständigen Panoramas')
    parser.add_argument('--picture', action='store_true', help='Schieße ein aktuelles Bild aus der aktuellen Position')
    parser.add_argument('--move', action='store_true', help='Bewegung der Kamera')

    args = parser.parse_args()
    print(args)
    c.take_picture()