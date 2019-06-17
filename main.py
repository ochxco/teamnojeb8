import webapp2
import jinja2
import os
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

#mainpage just to redirect users
class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect('/homepage')
        else:
            self.redirect('/login')

#prompts user to login
class NoUserHandler(webapp2.RequestHandler):
    def get(self):
        login_url = users.create_login_url("/")
        self.response.write('Please log in. <a href="' + login_url + '">Click here to login</a>')

#user is loggedin
class LoggedInHandler(webapp2.RequestHandler):
    def get(self):
        hometemplate = JINJA_ENVIRONMENT.get_template('templates/home.html')
        user = users.get_current_user()
        email = user.nickname()

        logout_url = users.create_logout_url("/")

        self.response.write("Hello " + email + '. You are logged in. <a href="' + logout_url + '">Click here to log out</a>')
        self.response.write(hometemplate.render())

class SearchBarHandler(webapp2.RequestHandler):
    def get(self):
        searchtemplate = JINJA_ENVIRONMENT.get_template('templates/search.html')
        self.response.write(searchtemplate.render())

app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/login', NoUserHandler),
    ('/homepage', LoggedInHandler),
    ('/search', SearchBarHandler),
], debug=True)