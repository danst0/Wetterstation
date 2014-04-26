#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import subprocess
import argparse
import os
import D3.pipan
import shutil

local_path = '/home/danst/Wetterstation/'
raspistill = '/opt/vc/bin/raspistill'
convert = '/usr/bin/convert'
class Camera:
    def __init__(self, rotation=180):
        self.rotation = rotation
        self.servos = D3.pipan.PiPan() 
        self.start_cam_x = 40
        self.max_cam_x = 180
        self.start_cam_y = 140
        self.max_cam_y = 140
        
    
    def take_picture(self, light=False):
        if not light:
            print('Schiesse Foto')
        image_raw = local_path + 'webcamraw.jpg'
        image = local_path + 'webcam.jpg'
        image_pan_temp = local_path + 'webcam_pan.jpg'
        image_pan_select = local_path + 'webcam_pan.jpg'
        image_pan_orig = local_path + 'webcam_pan_orig.jpg'
        image_pan_final = local_path + 'webcam_panorama.jpg'
        command = [raspistill, '-o', image_raw, '-t', '1']
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        if light:
            command = [convert, image_raw, '-rotate', str(self.rotation), image]
            try:
                output = subprocess.check_output(command, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError, e:
                print 'Fehler bei der Drehung des Bildes', e.returncode
                print e.output
                return False
        if not light:
            print 'Ergänzen Bildunterschrift, konvertieren, normalisieren, drehen'
            command = [convert, image_raw, '-normalize', '-rotate', str(self.rotation), '-pointsize', '72', '-fill', 'white', '-gravity', 'SouthWest', '-annotate', '+50+100', 'D3 Wetterstation %[exif:DateTimeOriginal]', image]
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
            print 'Erstellen Zuschnitt für Webseite'
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
    def move_picture(self):
        counter = 0
        for counter in range(15):
            filename = local_path + 'pano' + str(counter) + '.jpg'
            if os.path.isfile(filename):
                continue
            else:
                shutil.move(local_path + 'webcam.jpg', filename)
                break
    def delete_pano(self):
        for counter in range(15):
            filename = local_path + 'pano' + str(counter) + '.jpg'
            if os.path.isfile(filename):
                os.remove(filename)
    def take_panorama(self):
        self.delete_pano()
        self.servos.do_tilt(int(self.start_cam_y))
        self.servos.do_pan (self.start_cam_x)
#         for tilt in xrange(self.start_cam_y, self.max_cam_x, 20):
#             p.do_tilt (int(tilt))
        for pan in xrange(self.start_cam_x, self.max_cam_x, 40):
            self.servos.do_pan(int(pan))
            self.take_picture(light=True)
            self.move_picture()
        print 'Füge Bilder zusammen'
        img_list = []
        for counter in range(15):
            filename = local_path + 'pano' + str(counter) + '.jpg'
            if os.path.isfile(filename):
                img_list.append(filename)
                
        command = [convert, img_list, '-normalize', '-rotate', str(self.rotation), '+append', image]
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            print 'Fehler bei der Zusammenfügung der Bilder', e.returncode
            print e.output
            return False

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