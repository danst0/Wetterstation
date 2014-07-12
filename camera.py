#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import subprocess
import argparse
import os
import D3.pipan
import D3.config
import shutil
import pickle

local_path = '/home/danst/Wetterstation/'
raspistill = '/opt/vc/bin/raspistill'
convert = '/usr/bin/convert'
class Camera:
    def __init__(self, rotation=0):
        self.rotation = rotation
        self.servos = D3.pipan.PiPan(smooth=True) 
        self.start_cam_x = 40
        self.max_cam_x = 200
        self.start_cam_y = 140
        self.max_cam_y = 140
        cam_pos_one_way = [
                        (40, 130),
                        (40, 150),
                        (85, 150),
                        (85, 130),                        
                        (120, 130),
                        (120, 150),
                        (160, 130),
                        (195, 130),
                        (215, 130),
                        (240, 110),
                        (240, 200)]
        self.cam_pos = cam_pos_one_way[1:-1] + list(reversed(cam_pos_one_way))
        try:
            self.cam_pos_counter = pickle.load(open(D3.config.FULL_BASE_PATH + 'cam_pos.pickle', 'rb'))
        except:
            self.cam_pos_counter = 0
        self.last_pos_x = self.cam_pos[self.cam_pos_counter][0]
        self.last_pos_y = self.cam_pos[self.cam_pos_counter][1]

    
    def take_picture(self, light=False):
        if not light:
            self.move_next()
            print('Schiesse Foto')
        image_raw = local_path + 'webcamraw.jpg'
        image = local_path + 'webcam.jpg'
        image_pan_temp = local_path + 'webcam_pan.jpg'
        image_pan_select = local_path + 'webcam_pan.jpg'
        image_pan_orig = local_path + 'webcam_pan_orig.jpg'
        image_pan_final = local_path + 'webcam_panorama.jpg'
        command = [raspistill, '-o', image_raw, '--rotation', '180', '-t', '0']
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
        for pan in xrange(self.start_cam_x, self.max_cam_x, 50):
            self.servos.do_pan(int(pan))
            self.take_picture(light=True)
            self.move_picture()
        print 'Füge Bilder zusammen'
        img_list = []
        for counter in range(15):
            filename = local_path + 'pano' + str(counter) + '.jpg'
            if os.path.isfile(filename):
                img_list.append(filename)
#                 '-normalize', '-rotate', str(self.rotation), 
        command = [convert] + img_list + ['+append', local_path + 'webcam.jpg']
        print command
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            print 'Fehler bei der Zusammenfügung der Bilder', e.returncode
            print e.output
            return False
        self.delete_pano()

    def move_next(self):
        self.last_pos_x = self.cam_pos[self.cam_pos_counter][0]
        self.last_pos_y = self.cam_pos[self.cam_pos_counter][1]
        self.cam_pos_counter += 1
        if self.cam_pos_counter >= len(self.cam_pos):
            self.cam_pos_counter = 0
        self.servos.do_pan(self.cam_pos[self.cam_pos_counter][0], self.last_pos_x)
        self.servos.do_tilt(self.cam_pos[self.cam_pos_counter][1], self.last_pos_y)
        pickle.dump(self.cam_pos_counter, open(D3.config.FULL_BASE_PATH + 'cam_pos.pickle', 'wb'))


if __name__ == "__main__":
    c = Camera()
    parser = argparse.ArgumentParser(description='Kamera')
    parser.add_argument('--fullpanorama', action='store_true', help='Aufnahme eines vollständigen Panoramas')
    parser.add_argument('--picture', action='store_true', help='Schieße ein aktuelles Bild aus der aktuellen Position')
    parser.add_argument('--move', action='store_true', help='Bewegung der Kamera')
    
    args = parser.parse_args()
#     print(args)
#     while True:
#         c.move_next()
#         print c.cam_pos_counter, c.cam_pos[c.cam_pos_counter]
#         raw_input()
    if args.picture:
        c.take_picture()
    if args.fullpanorama:
        c.take_panorama()