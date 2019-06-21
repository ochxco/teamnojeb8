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
    profileimage=self.request.get('image')
    d = MangaUser.query().filter(MangaUser.username == name).fetch()
    #print(d)
    if name =='':
        self.redirect('/loginagain')

    elif d == []:
        manga_user = MangaUser(
            username=self.request.get('username'),
            email=user.nickname(),
            profile_img=profileimage,
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

        self.response.write('ERROR: You did not enter a username/Your username is already taken. <a href="' + login_url + '">Click here to login</a>')
    #def get(self):
        #login_url = users.create_login_url("/")
        #self.response.write('Please log in. <a href="' + login_url + '">Click here to login</a>')

class NoUserHandler(webapp2.RequestHandler):
    def get(self):
        logintemplate = JINJA_ENVIRONMENT.get_template('templates/loginbutton.html')
        d={'login_url':users.create_login_url("/"),}
        self.response.write(logintemplate.render(d))

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
                h={}
                j={}
                k={}
                l={}
                avg={}
                listofrandom=[]
                list=[]
                rec=[]
                mangas=Manga.query().fetch()
                print(rec)
                # print(manga_user.favorites.keys())
                if mangas!=[]:
                    for i in range(len(mangas)):
                        if mangas[i].total_ratings.keys() !=[]:
                            j[mangas[i].manga_id]=[]

                    for i in range(len(mangas)):
                        if mangas[i].total_ratings.keys() !=[]:
                            for ind in mangas[i].total_ratings.keys():
                                if ind in manga_user.friends_list:
                                    # print(mangas[i].total_ratings)
                                    # print(mangas[i].manga_id)
                                    j[mangas[i].manga_id].extend(mangas[i].total_ratings.values())

                            for ind in mangas[i].total_ratings.keys():
                                if ind == manga_user.username:
                                    del j[mangas[i].manga_id]
                    for i in range(len(mangas)):
                        if mangas[i].api_ratings!='None':
                            apirating=float(mangas[i].api_ratings[:3])
                            k[mangas[i].manga_id]=apirating
                    if len(k)>=10:

                        avg=calculateaverage(j)
                        print(avg)
                        count1=getgoodfrendrec(avg)
                        diff=0
                        print(count1)
                        if count1 >10:
                            rec=getmaxvalues(avg,10)
                        elif count1==0:
                            for i in range(len(mangas)):
                                if mangas[i].api_ratings!='None':
                                    apirating=float(mangas[i].api_ratings[:3])
                                    k[mangas[i].manga_id]=apirating

                                for ind in mangas[i].total_ratings.keys():
                                    if ind == manga_user.username:
                                        del k[mangas[i].manga_id]
                                # print(k.values())
                            rec.extend(getmaxvalues(k,10))
                        else:
                            # print(avg.values())
                            rec=getmaxvalues(avg,count1)
                            # print(rec)
                            diff=10-count1
                            for i in range(len(mangas)):
                                if mangas[i].api_ratings!='None':
                                    apirating=float(mangas[i].api_ratings[:3])
                                    if mangas[i].manga_id not in rec:
                                        k[mangas[i].manga_id]=apirating
                                for ind in mangas[i].total_ratings.keys():
                                    if ind == manga_user.username:
                                        del k[mangas[i].manga_id]
                            rec.extend(getmaxvalues(k,diff))
                        print(rec)
                if mangas !=[]:
                    for i in range(len(mangas)):
                        if mangas[i].manga_id in rec:
                            l[i]=[mangas[i].imgurl,mangas[i].manga_title,mangas[i].manga_id]




                d['h']=h
                d['l']=l
                for i in range(len(mangausers)):
                    if mangausers[i].username not in manga_user.friends_list:
                        e[i]={'key':mangausers[i].key,
                              'username': mangausers[i].username,
                              'rating':mangausers[i].user_ratings,
                              'reviews':mangausers[i].user_reviews,
                              'profile':mangausers[i].profile_img}
                        listofrandom.append(i)
                # print(d['e'][0]['key'].id())
                if len(e)-10>0:
                    while len(list) <10:
                        int = random.choice(listofrandom)
                        if int not in list:
                            list.append(int)
                    for i in range(len(list)):
                        g[i] = e[list[i]]
                    d['e']=g
                else:
                    d['e']=e
                d['username']=manga_user.username
                self.response.write(hometemplate.render(d))
            else:
                self.response.write('Please sign up for our page')
        else:
            self.response.write("Sorry, this page is only for logged in users.")

class SearchBarHandler(webapp2.RequestHandler):
    def post(self):
        searchtemplate = JINJA_ENVIRONMENT.get_template('templates/tryanime1.html')
        searchTerm=self.request.get('search')
        searchTerm=searchTerm.replace(' ','%20')
        user = users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
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
        dd = {'d': d, 'e':error,'username':manga_user.username,}
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
        if count !=0:
            averageuserrating=round((totalrating/count),1)
            friendrating=str(averageuserrating)+'/10'
        d['averageuserrating']=friendrating

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

        if name not in manga_user.favorites:
            favoritetext='Add to favorites'
        else:
            favoritetext='Added to favorites'
        # print(manga_user)
        d['favoritetext']=favoritetext
        d['username']=manga_user.username
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

        if name in manga_user.user_ratings:
            text = 'You have already rated this manga. Do you want to rate this again?'
        else:
            text = 'Rate this manga'
        d['info'].append(text)
        d['username']=manga_user.username
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
        h={}
        name1 = int(name)
        for i in range(len(mangauser)):
            if mangauser[i].key.id() == name1:
                d={'usernames': mangauser[i].username, 'id':name1, 'image': mangauser[i].profile_img}
                for j in range(len(mangauser[i].favorites.keys())):
                    mangaquery=Manga.query().filter(mangauser[i].favorites.keys()[j]==Manga.manga_id).get()
                    if mangaquery:
                        h[i]=[mangaquery.imgurl,mangaquery.manga_title,mangaquery.manga_id]
        d['h']=h
        if d['usernames'] not in manga_user.friends_list:
            text = "Click to follow user"
        else:
            text='Following. Click to Unfollow'
        d['text']=text
        d['logout']=logout_url
        d['username']=manga_user.username
        self.response.write(friendtemplate.render(d))
    def post(self,name):
        friendtemplate = JINJA_ENVIRONMENT.get_template('templates/friend.html')
        user = users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
        logout_url = users.create_logout_url("/")
        mangauser=MangaUser.query().fetch()
        text=''
        d={}
        h={}
        name1 = int(name)
        for i in range(len(mangauser)):
            if mangauser[i].key.id() == name1:
                d={'usernames': mangauser[i].username, 'id':name1, 'friend':mangauser[i], 'image':mangauser[i].profile_img}
                for j in range(len(mangauser[i].favorites.keys())):
                    mangaquery=Manga.query().filter(mangauser[i].favorites.keys()[j]==Manga.manga_id).get()
                    if mangaquery:
                        h[i]=[mangaquery.imgurl,mangaquery.manga_title,mangaquery.manga_id]
        d['h']=h
        if d['usernames'] not in manga_user.friends_list:
            manga_user.followfriend(d['friend'])
            text='Following. Click to unfollow'
        else:
            manga_user.removefriend(d['friend'])
            text='Click to follow user'
        manga_user.put()
        #print(manga_user)
        d['text']=text
        d['logout']=logout_url
        d['username']=manga_user.username
        self.response.write(friendtemplate.render(d))

class OwnProfileHandler(webapp2.RequestHandler):
    def get(self):
        ownproftemplate = JINJA_ENVIRONMENT.get_template('templates/ownprofile.html')
        user=users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
        mangausers = MangaUser.query().filter(MangaUser.email != user.nickname()).fetch()
        h={}
        f={}
        for i in range(len(manga_user.favorites.keys())):
            mangaquery=Manga.query().filter(manga_user.favorites.keys()[i]==Manga.manga_id).get()
            if mangaquery:
                h[i]=[mangaquery.imgurl,mangaquery.manga_title,mangaquery.manga_id]
        logout_url = users.create_logout_url("/")
        d = {}
        for i in range(len(mangausers)):
            if mangausers[i].username in manga_user.friends_list:
                f[i]={'key':mangausers[i].key,
                      'username': mangausers[i].username,
                      'rating':mangausers[i].user_ratings,
                      'reviews':mangausers[i].user_reviews,
                      'profile':mangausers[i].profile_img}

        d={'username':manga_user.username,'image':manga_user.profile_img }
        d['h']=h
        d['f']=f
        d['logout']=logout_url
        self.response.write(ownproftemplate.render(d))
    def post(self):
        ownproftemplate = JINJA_ENVIRONMENT.get_template('templates/ownprofile.html')
        user=users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
        mangausers = MangaUser.query().filter(MangaUser.email != user.nickname()).fetch()
        logout_url = users.create_logout_url("/")
        d = {}
        profileimg=self.request.get('profile_img')
        if profileimg=='':
            pass
        else:
            manga_user.profile_img=profileimg

        manga_user.put()
        h={}
        for i in range(len(manga_user.favorites.keys())):
            mangaquery=Manga.query().filter(manga_user.favorites.keys()[i]==Manga.manga_id).get()
            if mangaquery:
                h[i]=[mangaquery.imgurl,mangaquery.manga_title,mangaquery.manga_id]
        logout_url = users.create_logout_url("/")
        d = {}
        d={'username':manga_user.username,'image':manga_user.profile_img }
        d['h']=h
        f={}

        for i in range(len(mangausers)):
            if mangausers[i].username in manga_user.friends_list:
                f[i]={'key':mangausers[i].key,
                      'username': mangausers[i].username,
                      'rating':mangausers[i].user_ratings,
                      'reviews':mangausers[i].user_reviews,
                      'profile':mangausers[i].profile_img}
        d['f']=f
        d['logout']=logout_url
        self.response.write(ownproftemplate.render(d))

class SettingsHandler(webapp2.RequestHandler):
    def get(self):
        settingstemplate = JINJA_ENVIRONMENT.get_template('templates/settings.html')
        self.response.write(settingstemplate.render())

class FindFriendHandler(webapp2.RequestHandler):
    def post(self):
        friendtemplate = JINJA_ENVIRONMENT.get_template('templates/searchfriend.html')

        searchTerm=self.request.get('friend')
        user=users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
        logout_url = users.create_logout_url("/")
        user = users.get_current_user()
        manga_user=MangaUser.query().filter(MangaUser.email == user.nickname()).get()
        mangausers=MangaUser.query().filter(MangaUser.email != user.nickname()).fetch()
        error=''
        f={}
        for i in range(len(mangausers)):
            if searchTerm in mangausers[i].username:
                f[i]={'usernames': mangausers[i].username, 'id':mangausers[i].key.id(), 'image': mangausers[i].profile_img}

        if len(f)==0:
            error='No username found'



        #print(d)
        dd = {'f': f, 'e':error, 'logout':logout_url,'username':manga_user.username}


        self.response.write(friendtemplate.render(dd))


def calculateaverage(dict):
    avg={}
    for key,value in dict.items():
        avg[key]=0
        if value==[]:
            value=[0]
        for i in range(len(value)):
            avg[key]=avg[key]+value[i]
        avg[key]=round(avg[key]/len(value),1)
    return avg

def getmaxvalues(dict,no):
    count = 0
    maxdict=[]
    while count <= no:
        max1=max(dict.values())
        key1=''
        for key,value in dict.items():
            if value == max1:
                key1=key
        del dict[key1]
        maxdict.append(key1)
        count =count +1
    return (maxdict)

def getgoodfrendrec(dict):
    count = 0
    for key,value in dict.items():
        if value>8.0:
            count =count+1
    return count

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
    ('/searchfriend',FindFriendHandler),
], debug=True)
