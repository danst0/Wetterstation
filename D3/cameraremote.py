#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import shutil
import os
import pdb
import datetime
import pickle
import D3.config

class Camera:
    def __init__(self):
        self.camera_ip = 'sigma'
        self.local_folder = '/home/danst/Wetterstation/html/webcam/'
        self.remote_folder = '/home/danst/Wetterstation/'
        self.remote_user = 'danst'
        self.name_small_file = 'webcam.jpg'
        self.name_large_file = 'webcam_panorama.jpg'
        try:
            self.last_time = pickle.load(open(D3.config.FULL_BASE_PATH + 'camera.pickle', 'rb'))
        except:
            self.last_time = 0
    def rotate_pictures(self):
        basename_small = self.name_small_file[:self.name_small_file.rfind('.')]
        basename_large = self.name_large_file[:self.name_large_file.rfind('.')]
        D3.config.logging.debug(basename_small)
        D3.config.logging.debug(basename_large)
#         pdb.set_trace()
        for filename in [{'base':basename_small, 'all': self.name_small_file},{'base':basename_large, 'all': self.name_large_file}]:
            for i in range(22,0,-1):
#                 print i
                if os.path.isfile(self.local_folder+filename['base']+'-'+str(i)+'.jpg'):
#                     print 'moving', filename['base']+'-'+str(i)+'.jpg', filename['base']+'-'+str(i+1)+'.jpg'
                    shutil.move(self.local_folder+filename['base']+'-'+str(i)+'.jpg', self.local_folder+filename['base']+'-'+str(i+1)+'.jpg')
            shutil.move(self.local_folder+filename['all'], self.local_folder+filename['base']+'-1.jpg')

    def is_hourly_picture(self):
        next_hour = False
#         pdb.set_trace()
        if datetime.datetime.now().hour != self.last_time:
            next_hour = True
            self.last_time = datetime.datetime.now().hour
            pickle.dump(self.last_time, open(D3.config.FULL_BASE_PATH + 'camera.pickle', 'wb'))
        return next_hour
    def sshexec(self, command):
#         print(command)
        success = True
        try:
            p = subprocess.check_call(command, stdin=None, stdout=None, stderr=None)
        except subprocess.CalledProcessError as e:
            D3.config.logging.error(e)
            success = False
        return success
        
#     def download_picture(self):
#         command = ['/usr/bin/scp', self.remote_user+'@'+self.camera_ip+':' + self.remote_folder+self.name_small_file, self.local_folder]
#         self.sshexec(command)

    def download_panorama(self):
        command = ['/usr/bin/scp', self.remote_user+'@'+self.camera_ip+':'+self.remote_folder+'panorama.png', self.local_folder]
        self.sshexec(command)


    def download_picture(self):
        if self.is_hourly_picture():
            self.rotate_pictures()
        command = ['/usr/bin/scp', self.remote_user+'@'+self.camera_ip+':'+self.remote_folder+self.name_small_file, self.local_folder]
        self.sshexec(command)
        command = ['/usr/bin/scp', self.remote_user+'@'+self.camera_ip+':'+self.remote_folder+self.name_large_file, self.local_folder]
        self.sshexec(command)

        
    def take_picture(self):
        command = ['/usr/bin/ssh', self.remote_user+'@'+self.camera_ip, self.remote_folder+'camera.py', '--picture']
        tmp = self.sshexec(command)
        return tmp

    def alternative_picture(self):
        shutil.copyfile(self.local_folder+'webcam_icon.jpg', self.local_folder+self.name_small_file)
        shutil.copyfile(self.local_folder+'webcam_icon.jpg', self.local_folder+self.name_large_file)    
    def take_full_panorama(self):
        command = ['/usr/bin/ssh', self.remote_user+'@'+self.camera_ip, self.remote_folder+'camera.py',      '--fullpanorama']
        self.sshexec( )   
        return True

    def move_camera(self, delta_x=0, delta_y=0):
        direction = []
        if delta_x != 0:
            direction.append('--x '+str(delta_x))
        if delta_y != 0:
            direction.append('--y '+str(delta_y))
        command = ['/usr/bin/ssh', self.remote_user+'@'+self.camera_ip, self.remote_folder+'camera.py', '--move'] + direction
        self.sshexec(command)


if __name__ == "__main__":
    c = Camera()
    c.move_camera(delta_x=10, delta_y=10)
    c.take_picture()
        