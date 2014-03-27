#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import subprocess
import argparse
import os

local_path = '/home/danst/Wetterstation/'
raspistill = '/opt/vc/bin/raspistill'
convert = '/usr/bin/convert'
class Camera:
    def __init__(self, rotation=180):
        self.rotation = rotation
    def take_picture(self):
        print('Schiesse Foto')
        image_raw = local_path + 'webcamraw.jpg'
        image = local_path + 'webcam.jpg'
        image_pan_temp = local_path + 'webcam_pan.jpg'
        image_pan_select = local_path + 'webcam_pan.jpg'
        image_pan_orig = local_path + 'webcam_pan_orig.jpg'
        image_pan_final = local_path + 'webcam_panorama.jpg'
        command = [raspistill, '-o', image_raw, '-t', '1']
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
#         command = [convert, image_raw, '-pointsize 72', '-fill white', '-gravity SouthWest', "-annotate +50+100 'D3 Wetterstation %[exif:DateTimeOriginal]'", image]
#         command = [convert, image_raw, '-resize', '80%', image]
#         try:
#             output = subprocess.check_output(command, stderr=subprocess.STDOUT)
#         except subprocess.CalledProcessError, e:
#             print 'Fehler bei der Konvertierung', e.returncode
#             print e.output
#             return False
# #         print output
        print 'Ergänze Bildunterschrift, konvertieren, normalisieren, drehen'
        command = [convert, image_raw, '-pointsize', '72', '-fill', 'white', '-gravity', 'SouthWest', '-annotate', '+50+100', 'D3 Wetterstation %[exif:DateTimeOriginal]', '-normalize', '-rotate', str(self.rotation), image]
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            print 'Fehler bei der Ergänzung der Titel', e.returncode
            print e.output
            return False
#         print output        
#         convert -crop 100%x50% 0017kh.gif +repage  tiles%d.gif
#         2592x1944
        size_x = 2592
        size_y = 1944
        percentage = 0.60
        command = [convert, image, '-crop', str(size_x)+'x'+str(int(size_y*percentage))+'+0+'+str(size_y-int(size_y*percentage)), image_pan_temp]
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            print 'Fehler bei der Halbierung', e.returncode
            print e.output
            return False
#         print output     
#         try:
#             os.rename(image_pan_select, image_pan_orig)
#         except:
#             print 'Fehler bei der Umbenennung'
#             return False
        command = [convert, image_pan_select, '-resize', '30%', image_pan_final]
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            print 'Fehler bei der Konvertierung', e.returncode
            print e.output
            return False

        print('Foto erstellt')
        return True
    def take_panorama(self):
        self.take_picture()
if __name__ == "__main__":
    c = Camera()
    parser = argparse.ArgumentParser(description='Kamera')
    parser.add_argument('--fullpanorama', action='store_true', help='Aufnahme eines vollständigen Panoramas')
    parser.add_argument('--picture', action='store_true', help='Schieße ein aktuelles Bild aus der aktuellen Position')
    parser.add_argument('--move', action='store_true', help='Bewegung der Kamera')

    args = parser.parse_args()
#     print(args)
    if args.picture:
        c.take_picture()
    if args.fullpanorama:
        c.take_panorama()