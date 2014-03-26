#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import shutil

class Camera:
    camera_ip = 'sigma'
    local_folder = '/home/danst/Wetterstation/html/webcam/'
    remote_folder = '/home/danst/Wetterstation/'
    remote_user = 'danst'

    def sshexec(self, command):
#         print(command)
        success = True
        try:
            p = subprocess.check_call(command, stdin=None, stdout=None, stderr=None)
        except subprocess.CalledProcessError as e:
            print e
            success = False
        return success
        
    def download_picture(self):
        command = ['/usr/bin/scp', self.remote_user+'@'+self.camera_ip+':' + self.remote_folder+'webcam.jpg', self.local_folder]
        self.sshexec(command)

    def download_panorama(self):
        command = ['/usr/bin/scp', self.remote_user+'@'+self.camera_ip+':'+self.remote_folder+'panorama.png', self.local_folder]
        self.sshexec(command)


    def download_picture(self):
        command = ['/usr/bin/scp', self.remote_user+'@'+self.camera_ip+':'+self.remote_folder+'webcam.jpg', self.local_folder]
        self.sshexec(command)
        command = ['/usr/bin/scp', self.remote_user+'@'+self.camera_ip+':'+self.remote_folder+'webcam_panorama.jpg', self.local_folder]
        self.sshexec(command)

        
    def take_picture(self):
        command = ['/usr/bin/ssh', self.remote_user+'@'+self.camera_ip, self.remote_folder+'camera.py', '--picture']
        tmp = self.sshexec(command)
        return tmp
    def alternative_picture(self):
        shutil.copyfile(self.local_folder+'webcam_icon.jpg', self.local_folder+'webcam.jpg')
        shutil.copyfile(self.local_folder+'webcam_icon.jpg', self.local_folder+'webcam_panorama.jpg')    
    def take_full_panorama(self):
        command = ['/usr/bin/ssh', self.remote_user+'@'+self.camera_ip, self.remote_folder+'camera.py', '--fullpanorama']
        self.sshexec(command)
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
        