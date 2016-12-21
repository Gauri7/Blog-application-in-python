#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import uuid

import webapp2
import os
import time
# import base64, M2Crypto
# import uuid, OpenSSL

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template



path = os.path.join(os.path.dirname(__file__), 'test.html')
signuppath = os.path.join(os.path.dirname(__file__), 'signup.html')
loginpath = os.path.join(os.path.dirname(__file__), 'login.html')
welcomepath = os.path.join(os.path.dirname(__file__), 'welcome.html')
blogpath = os.path.join(os.path.dirname(__file__), 'blogcreation.html')
contentpath = os.path.join(os.path.dirname(__file__), 'content.html')


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


class User(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    email = ndb.StringProperty()


class SecureUser(ndb.Model):
    username = ndb.StringProperty()
    sessionid = ndb.StringProperty()


class BlogDetails(ndb.Model):
    username = ndb.StringProperty()
    title = ndb.StringProperty()
    content = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    millis = ndb.IntegerProperty()

class Signup(Handler):
    def get(self):
        try:
            cookie_val = self.request.cookies.get("user")
            cookie_user = SecureUser.query().filter(SecureUser.sessionid == cookie_val).get();
            uname = cookie_user.username
            if cookie_user:
                self.redirect("/")

            else:
                template_values = {"error": ""}
                self.write(template.render(signuppath, template_values))
        except:
            template_values = {"error": ""}
            self.write(template.render(signuppath, template_values))

    def post(self):
        userName = self.request.get("username")
        passWord = self.request.get("password")
        Email = self.request.get("email")

        if (userName == "") and (passWord == ""):
            template_values = {"error": "fields cannot be empty"}
            self.write(template.render(signuppath, template_values))
        elif User.query().filter(User.username == userName).get():
            template_values = {"error": "Username already exisit"}
            self.write(template.render(signuppath, template_values))
        else:
            users = User(username=userName, password=passWord, email=Email, id=userName)
            users.put()
            template_values = {"user": userName}
            secure_cookie = uuid.uuid1()
            # self.write(secure_cookie)
            self.response.headers.add_header('Set-Cookie', '%s=%s' % ("user", str(secure_cookie)))
            cookies = SecureUser(username=userName, sessionid=str(secure_cookie), id=userName)
            cookies.put()
            blog = BlogDetails.query().order(-ndb.DateTimeProperty("created"))
            template_values = {"user": userName,
                               "blog": blog,
                               "username": userName,
                               }
            self.write(template.render(welcomepath, template_values))
            self.redirect("/")

class Login(Handler):
    def get(self):
        try:
            cookie_val = self.request.cookies.get("user")

            cookie_user = SecureUser.query().filter(SecureUser.sessionid == cookie_val).get();
            uname = cookie_user.username
            if cookie_user:

                self.redirect("/")
                #self.response.out.write("")

            else:
                template_values = {"error": ""}
                self.write(template.render(loginpath, template_values))

        except:
            template_values = {"error": ""}
            self.write(template.render(loginpath, template_values))

    def post(self):
        userName = self.request.get("username")
        passWord = self.request.get("password")
        if userName and passWord:
            # c = SecureUser.query().filter(SecureUser.username == userName).get()
            try:
                u = User.query().filter(User.username == userName).get()
                c = SecureUser.query().filter(SecureUser.username == userName).get()
                blog = BlogDetails.query().order(-ndb.DateTimeProperty("created"))

                if u.password == passWord:
                    ck = c.sessionid
                    cn = c.username

                    self.response.headers.add_header('Set-Cookie', '%s=%s' % ("user", str(ck)))

                    template_values = {"user": userName,
                                     "blog": blog,
                                      "username":userName,
                                      "cookiename": cn }
                    self.write(template.render(welcomepath, template_values))
                    blog = BlogDetails.query().order(-ndb.DateTimeProperty("created"))


                    cookie_val = self.request.cookies.get("user")

                    cookie_user = SecureUser.query().filter(SecureUser.sessionid == cookie_val).get();
                    uname = cookie_user.username
                    # if cookie_user:
                    template_values = {"user": uname}
                    self.write(template.render(welcomepath, template_values))

                else:
                    template_values = {"error": "Please enter vaild details"}
                    self.write(template.render(loginpath, template_values))

            except:
                template_values = {"error": ""}
                self.write(template.render(loginpath, template_values))


        else:
            template_values = {"error": "Please fill details"}
            self.write(template.render(loginpath, template_values))



class Logout(Handler):
    def get(self):
        blog = BlogDetails.query().order(-ndb.DateTimeProperty("created"))
        template_values = {"blog": blog}
        self.write(template.render(path, template_values))
        cookie_val = self.request.cookies.get("user")
        # self.response.headers.add_header('Set-Cookie', 'user=')
        self.response.delete_cookie('user')

    def post(self):
        cookie_val = self.request.cookies.get("user")
        self.response.headers.add_header('Set-Cookie', 'user=')
        self.response.delete_cookie(cookie_val)


class Create(Handler):
    def get(self):
        title = self.request.get("title")
        content = self.request.get("content")

        template_values = { "content": content,
                             "title": title

        }
        self.write(template.render(blogpath, template_values))

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        cookie_val = self.request.cookies.get("user")
        millis =int(round(time.time()*1000))
        cookie_user = SecureUser.query().filter(SecureUser.sessionid == cookie_val).get();
        uname = cookie_user.username

        blogs = BlogDetails(username=uname, title=title, content=content,millis=millis)
        blogs.put()
        blog = BlogDetails.query().order(-ndb.DateTimeProperty("created"))
        template_values = {"user": uname,
                           "blog": blog,
                           "username": uname,
                           }
        self.write(template.render(welcomepath, template_values))


class Blogs(Handler):
    def get(self, id):

        blogc = ndb.Key(BlogDetails,int(id)).get()
        title = blogc.title
        content = blogc.content
        name = blogc.username
        created = blogc.created
        try:
            cookie_val = self.request.cookies.get("user")

            cookie_user = SecureUser.query().filter(SecureUser.sessionid == cookie_val).get();
            uname = cookie_user.username
            template_values = {
                "content": content,
                "title": title,
                "username": name,
                "created": created,
                "cookie": uname,
                "id":id
            }
            self.write(template.render(contentpath, template_values))


        except:
            content = blogc.content
            name = blogc.username
            template_values = {
                "content": content,
                "title": title,
                "username": name,
                "created": created
            }
            self.write(template.render(contentpath, template_values))


class Edit(Handler):


    def get(self,id):
        #title = self.request.get("title")
        #content = self.request.get("content")
        blogs = ndb.Key(BlogDetails,int(id)).get()

        title = blogs.title
        content = blogs.content
        template_values = {
            "title": title,
            "content": content,
        }
        self.write(template.render(blogpath, template_values))

    def post(self,id):
        title = self.request.get("title")
        content = self.request.get("content")
        cookie_val = self.request.cookies.get("user")
        cookie_user = SecureUser.query().filter(SecureUser.sessionid == cookie_val).get()
        uname = cookie_user.username
        #keys = int(Edit.key)
        blogt = ndb.Key(BlogDetails,int(id)).get()
        #blogq = BlogDetails.get_by_id(str(Edit.key))
        blogt.title = title
        blogt.content = content
        blogt.put()
        blog = BlogDetails.query().order(-ndb.DateTimeProperty("created"))
        template_values = {"user": uname,
                           "blog": blog,
                           "username": uname,
                           }
        self.redirect("/")


class Delete(Handler):
    def get(self,id):


        cookie_val = self.request.cookies.get("user")

        cookie_user = SecureUser.query().filter(SecureUser.sessionid == cookie_val).get()
        uname = cookie_user.username
        blogs =  ndb.Key(BlogDetails, int(id)).get()
        name = blogs.username
        if cookie_val and uname==name:

            ndb.Key(BlogDetails, int(id)).delete()

            blog = BlogDetails.query().order(-ndb.DateTimeProperty("created"))
            template_values = {"user": uname,
                           "blog": blog,
                           "username": uname,
                           }
            self.write(template.render(welcomepath, template_values))

        else :
            self.write("You cant modify or delete other blogs")


class Test(Handler):
    def get(self):
        # self.render('test.html', error="")
        # template_values = {"error": ""}
        # self.write(template.render(path, template_values))
        try:
            cookie_val = self.request.cookies.get("user")
            cookie_user = SecureUser.query().filter(SecureUser.sessionid == cookie_val).get();
            uname = cookie_user.username
            if cookie_user:


                blog = BlogDetails.query().order(-ndb.DateTimeProperty("created"))
                template_values = {"user": uname,
                               "blog": blog
                               }
                self.write(template.render(welcomepath, template_values))

            else:

                blog = BlogDetails.query().order(-ndb.DateTimeProperty("created"))
                template_values = {"blog": blog}
                self.write(template.render(path, template_values))

        except:
            blog = BlogDetails.query().order(-ndb.DateTimeProperty("created"))
            template_values = {"blog": blog}
            self.write(template.render(path, template_values))

app = webapp2.WSGIApplication([('/', Test),
                               ('/signup', Signup),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/blogcreation', Create),
                               ('/blogs/(\d+)', Blogs),
                               #('/blog/<blog_id>', Blog)
                               ('/edit/(\d+)', Edit),
                               ('/delete/(\d+)', Delete)],
                              debug=True)
