import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.api import urlfetch
import json
from google.appengine.ext import ndb
from models import Manga, MangaUser

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

#mainpage just to redirect users
class MainPageHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    # If the user is logged in...
    if user:
      email_address = user.nickname()
      manga_user = MangaUser.query().filter(MangaUser.email == email_address).get()
      # If the user is registered...
      if manga_user:
        # Greet them with their personal information
        # self.response.write('''
        #     Welcome %s (%s)! <br> %s <br>''' % (
        #       manga_user.username,
        #       email_address,
        #       signout_link_html))
        self.redirect('/homepage')
      # If the user isn't registered...
      else:
        # Offer a registration form for a first-time visitor:
        self.response.write('''
            Welcome to our site, %s!  Please sign up! <br>
            <form method="post" action="/">
            <input type="text" name="username" placeholder='Enter a username...'>
            <input type="submit">
            </form>
            ''' % (email_address))
    else:
      # If the user isn't logged in...
      # login_url = users.create_login_url('/')
      # login_html_element = '<a href="%s">Sign in</a>' % login_url
      # # Prompt the user to sign in.
      # self.response.write('Please log in.<br>' + login_html_element)
      self.redirect('/login')

  def post(self):
    # Code to handle a first-time registration from the form:
    user = users.get_current_user()
    manga_user = MangaUser(
        username=self.request.get('username'),
        email=user.nickname(),
        user_ratings={},
        user_reviews={})
    manga_user.put()
    self.response.write('Thanks for signing up, %s! <br>Go to the <a href="/homepage">Home</a> page' %
        manga_user.username)



class NoUserHandler(webapp2.RequestHandler):
    def get(self):
        login_url = users.create_login_url("/")
        self.response.write('Please log in. <a href="' + login_url + '">Click here to login</a>')

#user is loggedin
class LoggedInHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            manga_user = MangaUser.query().filter(MangaUser.email == user.nickname()).get()
            # If the user is registered...
            if manga_user:
                hometemplate = JINJA_ENVIRONMENT.get_template('templates/homepage.html')
                logout_url = users.create_logout_url("/")
                d = {'logout': logout_url}
                manga_user = MangaUser.query().filter(MangaUser.email == user.nickname()).fetch()
                # print(manga_user)
                self.response.write("Hello " + manga_user[0].username + '. You are logged in.')
                self.response.write(hometemplate.render(d))
            else:
                self.response.write('Pls sign up for our page')
        else:
            self.response.write("Sorry, this page is only for logged in users.")

class SearchBarHandler(webapp2.RequestHandler):
    def post(self):
        searchtemplate = JINJA_ENVIRONMENT.get_template('templates/tryanime1.html')
        searchTerm=self.request.get('search')
        searchTerm=searchTerm.replace(' ','%20')
        endpoint_url='https://kitsu.io/api/edge/manga?page[limit]=20&filter[text]='+searchTerm
        response = urlfetch.fetch(endpoint_url)
        content = response.content
        response_as_json = json.loads(content)
        d={}
        if response_as_json['data']==[]:
            error='No manga found. Check your spelling'
        else:
            error=''
        for i in range(len(response_as_json['data'])):
            image_url=response_as_json['data'][i]['attributes']['posterImage']['medium']
            titles=response_as_json['data'][i]['attributes']['canonicalTitle']
            mangaid=response_as_json['data'][i]['id']
            d[i]=[image_url,titles,mangaid]
        #print(d)
        dd = {'d': d, 'e':error}
        self.response.write(searchtemplate.render(dd))
class MangaHandler(webapp2.RequestHandler):
    def get(self, name):
        mangatemplate = JINJA_ENVIRONMENT.get_template('templates/manga.html')
        # print (name)
        text=''
        user = users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
        if name in manga_user.user_ratings:
            text = 'You have already rated this manga. Do you want to rate this again?'
        else:
            text = 'Rate this manga'
        endpoint_url='https://kitsu.io/api/edge/manga/'+name
        # print(endpoint_url)
        response = urlfetch.fetch(endpoint_url)
        #print(response.status_code)
        content = response.content
        # print(content)
        response_as_json = json.loads(content)
        # print(response_as_json)
        d={}
        image_url=response_as_json['data']['attributes']['posterImage']['medium']
        titles=response_as_json['data']['attributes']['canonicalTitle']
        synopsis=response_as_json['data']['attributes']['synopsis']
        mangaid=response_as_json['data']['id']
        d['info']=[image_url,titles,synopsis,mangaid,text]
        # print(d)
        # print(manga_user)
        self.response.write(mangatemplate.render(d))
        manga = Manga(
            manga_id=d['info'][3],
            manga_title = d['info'][1],
            reviews={},
            total_ratings={},
        )
        manga.put()
    def post( self,name):
        # print(name)
        mangatemplate = JINJA_ENVIRONMENT.get_template('templates/manga.html')
        user = users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
        # print(manga_user.user_ratings)
        rating = self.request.get("rating")
        review = self.request.get('review')
        endpoint_url='https://kitsu.io/api/edge/manga/'+name

        # print(endpoint_url)
        response = urlfetch.fetch(endpoint_url)
        #print(response.status_code)
        content = response.content
        # print(content)
        response_as_json = json.loads(content)
        # print(response_as_json)
        d={}
        image_url=response_as_json['data']['attributes']['posterImage']['medium']
        titles=response_as_json['data']['attributes']['canonicalTitle']
        synopsis=response_as_json['data']['attributes']['synopsis']
        mangaid=response_as_json['data']['id']
        text = 'You have already rated this manga. Do you want to rate this again?'
        d['info']=[image_url,titles,synopsis,mangaid,text]
        # print(rating)
        if rating =='' and review =='':
            pass
        elif review =='':
            manga_user.user_ratings[name]=float(rating)
        else:
            manga_user.user_ratings[name]=float(rating)
            manga_user.user_reviews[name]=review

        # print(manga_user.user_ratings)
        manga_user.put()
        manga = Manga.query().filter(Manga.manga_title == d['info'][3]).fetch()
        print (manga)
        #manga.manga_id = name
        #manga.reviews.append(review)
        #manga.ratings.append(rating)
        #anga.put()
        for review in len(manga.reviews):
            pass
        self.response.write(mangatemplate.render(d))

def CalculateRating(manga_id,rating):
    Manga.total_ratings.append(rating)
    sum = 0
    for n in manga.total_ratings:
        sum += n
    Manga.average_ratings = sum
    Manga.put()


app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/login', NoUserHandler),
    ('/homepage', LoggedInHandler),
    ('/search', SearchBarHandler),
    ('/manga/(\w+)', MangaHandler),
], debug=True)
