#!/usr/bin/env python
# -*- coding: utf-8 -*-


PAGESIZE=50

import sys
import os
import code

SDK_DIR = r'D:\Program Files\Google\google_appengine'
EXTRA_PATHS = [
	SDK_DIR,
	os.path.join(SDK_DIR, 'lib', 'antlr3'),
	os.path.join(SDK_DIR, 'lib', 'django'),
	os.path.join(SDK_DIR, 'lib', 'webob'),
	os.path.join(SDK_DIR, 'lib', 'yaml', 'lib'),
        os.path.join(SDK_DIR, 'lib', 'fancy_urllib'),
]
sys.path = EXTRA_PATHS + sys.path

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db
import getpass
from models import Images

def auth_func():
    return raw_input('Username:'), getpass.getpass('Password:')

class BackUpPic():
    def __init__(self,appid):
        self.appid=appid

    def login(self):
        host = '%s.appspot.com' % self.appid
        remote_api_stub.ConfigureRemoteDatastore(self.appid, '/remote_api',auth_func, host)
    
    def backup(self):
        images=Images.all().fetch(PAGESIZE)
        while images:
            for image in images:
                self.save(image)
            images = Images.all().filter('__key__ >', images[-1].key()).fetch(PAGESIZE)
            
    def save(self,im):
        """
        save file,
        im is a image object
        """
        ft=im.mime.split('/')[1]
        filename="backup/%s.%s" %(im.key().id(),ft)
        with open(filename,'wb') as f:
            f.write(im.bf)
            f.close()
            print "%s backup success!" % filename
        
if __name__=='__main__':
    appid = raw_input('Please enter your appid:') 
    bk=BackUpPic(appid)
    bk.login()
    bk.backup()
    
