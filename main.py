import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.api import urlfetch
import json
from google.appengine.ext import ndb
from models import Manga, MangaUser
import random

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
        self.redirect('/homepage')
      # If the user isn't registered...
      else:
        # Offer a registration form for a first-time visitor:

        signuptemplate = JINJA_ENVIRONMENT.get_template('templates/signup.html')
        d={'email':email_address}
        self.response.write(signuptemplate.render(d))

    else:
      # If the user isn't logged in...
      self.redirect('/login')

  def post(self):
    # Code to handle a first-time registration from the form:
    user = users.get_current_user()
    name=self.request.get('username')
    d = MangaUser.query().filter(MangaUser.username == name).fetch()
    #print(d)
    if d == []:
        manga_user = MangaUser(
            username=self.request.get('username'),
            email=user.nickname(),
            profile_img="https://sketchmob.com/wp-content/uploads/2018/06/110748_1e7a40910-720x974.jpg",
            user_ratings={},
            user_reviews={},
            friends_list={},
            favorites={})
        manga_user.put()
        self.response.write('Thanks for signing up, %s! <br>Go to the <a href="/homepage">Home</a> page' %
                manga_user.username)
    else:
        self.redirect('/loginagain')


class Nametaken(webapp2.RequestHandler):
    def get(self):
        login_url = users.create_login_url("/")
        self.response.write('Your username is already taken. <a href="' + login_url + '">Click here to login</a>')
    #def get(self):
        #login_url = users.create_login_url("/")
        #self.response.write('Please log in. <a href="' + login_url + '">Click here to login</a>')

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
                manga_user = MangaUser.query().filter(MangaUser.email == user.nickname()).get()
                # print(manga_user)
                mangausers = MangaUser.query().filter(MangaUser.email != user.nickname()).fetch()
                # print(mangausers)
                g={}
                e={}
                f={}
                h={}
                listofrandom=[]
                list=[]
                print(manga_user.favorites.keys())
                if Manga.query().fetch()!=[]:
                    for i in range(len(manga_user.favorites.keys())):
                        mangaquery=Manga.query().filter(manga_user.favorites.keys()[i]==Manga.manga_id).get()
                        if mangaquery:
                            h[i]=[mangaquery.imgurl,mangaquery.manga_title,mangaquery.manga_id]

                d['h']=h
                for i in range(len(mangausers)):
                    if mangausers[i].username not in manga_user.friends_list:
                        e[i]={'key':mangausers[i].key,
                              'username': mangausers[i].username,
                              'rating':mangausers[i].user_ratings,
                              'reviews':mangausers[i].user_reviews}
                        listofrandom.append(i)
                    else:
                        f[i]={'key':mangausers[i].key,
                              'username': mangausers[i].username,
                              'rating':mangausers[i].user_ratings,
                              'reviews':mangausers[i].user_reviews}

                # print(d['e'][0]['key'].id())
                if len(e)-5>0:
                    while len(list) <5:
                        int = random.choice(listofrandom)
                        if int not in list:
                            list.append(int)
                    for i in range(len(list)):
                        g[i] = e[list[i]]
                    d['e']=g

                else:
                    d['e']=e

                d['f']=f

                self.response.write("Hello " + manga_user.username + '. You are logged in.')
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
        logout_url = users.create_logout_url("/")
        if name in manga_user.user_ratings:
            text = 'You have already rated this manga. Do you want to rate this again?'
        else:
            text = 'Rate this manga'
        d={}
        d['logout']=logout_url
        favoritetext=''
        friendrating='No ratings yet'
        d['reviews']={'No review yet':''}
        mangaquery = Manga.query().fetch()
        boolean=False
        totalrating= 0
        count=0
        for i in range(len(mangaquery)):
            if name == mangaquery[i].manga_id:
                manga = mangaquery[i]
                boolean =True
                d['info']=[manga.imgurl,manga.manga_title,manga.synopsis,manga.manga_id,manga.api_ratings,manga.chapter,text]
                if manga.total_ratings != {}:
                    for key,value in manga.total_ratings.items():
                        if key in manga_user.friends_list:
                            totalrating=totalrating+value
                            count = count +1
                if manga.reviews !={}:
                    d['reviews']=manga.reviews
                break;
            else:
                boolean=False

        # print(d['reviews'])
        if boolean == False:
            endpoint_url='https://kitsu.io/api/edge/manga/'+name
            response = urlfetch.fetch(endpoint_url)
            content = response.content
            response_as_json = json.loads(content)
            image_url=response_as_json['data']['attributes']['posterImage']['medium']
            titles=response_as_json['data']['attributes']['canonicalTitle']
            synopsis=response_as_json['data']['attributes']['synopsis']
            mangaid=response_as_json['data']['id']
            averagerating=response_as_json['data']['attributes']['averageRating']
            chapter=response_as_json['data']['attributes']['chapterCount']
            if averagerating>0:
                averageratin=str(round(float(averagerating)/10,1))+'/10'
            else:
                averageratin='None'

            d['info']=[image_url,titles,synopsis,mangaid,averageratin,chapter, text]
            manga = Manga(
                 manga_id=mangaid,
                 manga_title = titles,
                 imgurl=image_url,
                 synopsis=synopsis,
                 reviews={},
                 total_ratings={},
                 api_ratings=averageratin,
                 chapter=chapter,
            )
            manga.put()
        if count !=0:
            averageuserrating=round((totalrating/count),1)
            friendrating=str(averageuserrating)+'/10'

        if name not in manga_user.favorites:
            favoritetext='Add to favorites'
        else:
            favoritetext='Added to favorites'
        # print(manga_user)
        d['favoritetext']=favoritetext
        d['averageuserrating']=friendrating

        self.response.write(mangatemplate.render(d))

    def post(self,name):
        # print(type(name))
        mangatemplate = JINJA_ENVIRONMENT.get_template('templates/manga.html')

        user = users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
        logout_url = users.create_logout_url("/")
        d={}
        totalrating= 0
        count=0
        favoritetext=''
        d['reviews']={'No review yet':''}
        friendrating='No ratings yet'
        mangaquery=Manga.query().fetch()
        for i in range(len(mangaquery)):
            if name == mangaquery[i].manga_id:
                manga = mangaquery[i]
                d['info']=[manga.imgurl,manga.manga_title,manga.synopsis,manga.manga_id,manga.api_ratings,manga.chapter]
                if manga.total_ratings != {}:
                    for key,value in manga.total_ratings.items():
                        if key in manga_user.friends_list:
                            totalrating=totalrating+value
                            count = count +1
                if manga.reviews !={}:
                    d['reviews']=manga.reviews
        print(manga.reviews)
        if count !=0:
            averageuserrating=round((totalrating/count),1)
            friendrating=str(averageuserrating)+'/10'
        d['averageuserrating']=friendrating

        if name not in manga_user.favorites:
            favoritetext='Add to favorites'
        else:
            favoritetext='Added to favorites'
        if 'favorites' in self.request.POST:
            if name not in manga_user.favorites:
                manga_user.favorites[name]=[manga.manga_title, manga.imgurl]
                favoritetext='Added to favorites'
            else:
                del manga_user.favorites[name]
                favoritetext='Add to favorites'
            manga_user.put()
        else:
            rating = self.request.get("rating")
            reviews = self.request.get('review')
            text = 'You have already rated this manga. Do you want to rate this again?'
            d['info'].append(text)
            if rating =='' and reviews =='':
                pass
            elif reviews =='':
                manga_user.user_ratings[name]=float(rating)
                manga.total_ratings[manga_user.username]=float(rating)
            else:
                manga_user.user_ratings[name]=float(rating)
                manga_user.user_reviews[name]=reviews
                manga.total_ratings[manga_user.username]=float(rating)
                manga.reviews[manga_user.username]= reviews
            manga_user.put()
            manga.put()


        d['logout']=logout_url
        d['favoritetext']=favoritetext
        self.response.write(mangatemplate.render(d))

class FriendHandler(webapp2.RequestHandler):
    def get(self,name):
        friendtemplate = JINJA_ENVIRONMENT.get_template('templates/friend.html')
        user = users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
        logout_url = users.create_logout_url("/")
        mangauser=MangaUser.query().fetch()
        text=''
        d={}
        name1 = int(name)
        for i in range(len(mangauser)):
            if mangauser[i].key.id() == name1:
                d={'username': mangauser[i].username, 'id':name1, 'image': mangauser[i].profile_img}
        if d['username'] not in manga_user.friends_list:
            text = "Click to follow user"
        else:
            text='Following. Click to Unfollow'
        d['text']=text
        d['logout']=logout_url
        self.response.write(friendtemplate.render(d))
    def post(self,name):
        friendtemplate = JINJA_ENVIRONMENT.get_template('templates/friend.html')
        user = users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
        logout_url = users.create_logout_url("/")
        mangauser=MangaUser.query().fetch()
        text=''
        d={}
        name1 = int(name)
        for i in range(len(mangauser)):
            if mangauser[i].key.id() == name1:
                d={'username': mangauser[i].username, 'id':name1, 'friend':mangauser[i], 'image':mangauser.profile_img}
        if d['username'] not in manga_user.friends_list:
            manga_user.followfriend(d['friend'])
            text='Following. Click to unfollow'
        else:
            manga_user.removefriend(d['friend'])
            text='Click to follow user'
        manga_user.put()
        #print(manga_user)
        d['text']=text
        d['logout']=logout_url
        self.response.write(friendtemplate.render(d))

class OwnProfileHandler(webapp2.RequestHandler):
    def get(self):
        ownproftemplate = JINJA_ENVIRONMENT.get_template('templates/ownprofile.html')
        user=users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
        logout_url = users.create_logout_url("/")
        d = {}
        d={'username':manga_user.username,'image':manga_user.profile_img }
        d['logout']=logout_url
        self.response.write(ownproftemplate.render(d))

class SettingsHandler(webapp2.RequestHandler):
    def post(self):
        settingstemplate = JINJA_ENVIRONMENT.get_template('templates/settings.html')
        user=users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
        logout_url = users.create_logout_url("/")
        d={}
        manga_user.profile_img(self.request.get('profile_img'))
        manga_user.background_img(self.request.get('background_img'))
        self.response.write(settingstemplate.render())

def CalculateRating(manga_id,rating):
    Manga.total_ratings.append(rating)
    sum = 0
    for n in manga.total_ratings:
        sum += n
    Manga.average_ratings = sum
    Manga.put()

def generaterandom(length):
    listofrandom=[]
    while len(listofrandom)<5:
        no= random.randint(0,length-1)
        if no not in listofrandom:
            listofrandom.append(no)
    return (listofrandom)


app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/login', NoUserHandler),
    ('/homepage', LoggedInHandler),
    ('/search', SearchBarHandler),
    ('/manga/(\w+)', MangaHandler),
    ('/friend/(\w+)', FriendHandler),
    ('/loginagain', Nametaken),
    ('/profile', OwnProfileHandler),
    ('/editprofile', SettingsHandler),
], debug=True)
