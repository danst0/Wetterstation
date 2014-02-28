#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

class Camera:
    camera_ip = '192.168.1.1'
    local_folder = '/Users/danst/Documents/Archiv/Computer-Elektronik/'
    remote_folder = '/root/'
    remote_user = 'root'

    def sshexec(self, command):
        print(command)
        p = subprocess.check_call(command, stdin=None, stdout=None, stderr=None)
        
    def download_picture(self):
        command = ['/usr/bin/scp', remote_user+'@'+self.camera_ip+':'+remote_folder+'picture.png', local_folder]
        self.sshexec(command)

    def download_panorama(self):
        command = ['/usr/bin/scp', remote_user+'@'+self.camera_ip+':'+remote_folder+'panorama.png', local_folder]
        self.sshexec(command)


    def download_picture(self):
        command = ['/usr/bin/scp', remote_user+'@'+self.camera_ip+':'+remote_folder+'picture.png', local_folder]
        self.sshexec(command)

        
    def take_picture(self):
        command = ['/usr/bin/ssh', remote_user+'@'+self.camera_ip, remote_folder+'camera.py', '--picture']
        self.sshexec(command)
        
    def take_full_panorama(self):
        command = ['/usr/bin/ssh', remote_user+'@'+self.camera_ip, remote_folder+'camera.py', '--fullpanorama']
        self.sshexec(command)

    def move_camera(self, delta_x=0, delta_y=0):
        direction = []
        if delta_x != 0:
            direction.append('--x '+str(delta_x))
        if delta_y != 0:
            direction.append('--y '+str(delta_y))
        command = ['/usr/bin/ssh', remote_user+'@'+self.camera_ip, remote_folder+'camera.py', '--move'] + direction
        self.sshexec(command)


if __name__ == "__main__":
    c = Camera()
    c.move_camera(delta_x=10, delta_y=10)
    c.take_picture()
        