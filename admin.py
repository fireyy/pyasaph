#coding:utf-8
import sys
sys.path.append( "dropbox/"); 
import oauth,auth,client,rest
import wsgiref.handlers
import urllib2
import os
from functools import wraps
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
import methods,logging
from django.utils import simplejson

adminFlag=True

class AdminControl(webapp.RequestHandler):
    def render(self,template_file,template_value):
        path=os.path.join(os.path.dirname(__file__),template_file)
        self.response.out.write(template.render(path, template_value))
    def returnjson(self,dit):
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(simplejson.dumps(dit))
        
def requires_admin(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not users.is_current_user_admin() and adminFlag:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            return method(self, *args, **kwargs)
    return wrapper

class Admin_Upload(AdminControl):
    @requires_admin
    def get(self):
        title=self.request.get("title")
        referer=self.request.get("referer")
        image=self.request.get("image")
        xhrLocation=self.request.get("xhrLocation")
        self.render('views/upload.html', {"title":title,"referer":referer,"image":image,"xhrLocation":xhrLocation})
    @requires_admin
    def post(self):
        bf=self.request.get("image")
        if not bf:
            return self.redirect('/admin/upload/')
        o = urllib2.build_opener();
        f = o.open(bf).read();

        title=self.request.get("title")
        referer=self.request.get("referer")
        xhrLocation=self.request.get("xhrLocation")
        image=methods.addImage( title, f, referer)

        self.render('views/posted.html', {"msg":"success","xhrLocation":xhrLocation})
        
class Admin_read(AdminControl):
    @requires_admin
    def get(self):
        
        f = urllib2.urlopen('http://img1.cache.netease.com/cnews/2011/5/6/20110506083751ebe4c.jpg')
        image=methods.addImage("11111",f.read(),"http://1111")
        
        config = auth.Authenticator.load_config("config/dropbox.ini")
        dba = auth.Authenticator(config)
        #access_token = dba.obtain_trusted_access_token(config['testing_user'], config['testing_password'])
        access_token = oauth.OAuthToken.from_string("oauth_token_secret=f16we6l2pn4mkx5&oauth_token=299vslb2j8xg8ns")
        db_client = client.DropboxClient(config['server'], config['content_server'], config['port'], dba, access_token)
        root = config['root']
        
        image.name = "20110506083751ebe4c.jpg";
    
        resp = db_client.put_file(root, "/", image)
        print resp

class Delete_Image(AdminControl):
    @requires_admin
    def get(self,key):
        methods.delImage(key)
        self.redirect('/')
        
class Delete_Image_ID(AdminControl):
    @requires_admin
    def get(self,id):
        methods.delImageByid(id)
        self.redirect('/')

class Admin_Login(AdminControl):
    @requires_admin
    def get(self):
        self.redirect('/')
        
def main():
    application = webapp.WSGIApplication(
                                       [(r'/admin/upload/', Admin_Upload),
                                        (r'/admin/read/', Admin_read),
                                        (r'/admin/del/(?P<key>[a-z,A-Z,0-9,-]+)', Delete_Image),
                                        (r'/admin/delid/(?P<id>[0-9]+)/', Delete_Image_ID),
                                        (r'/admin/', Admin_Login),
                                       ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()