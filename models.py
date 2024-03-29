from google.appengine.ext import ndb

class Manga(ndb.Model):
    manga_id = ndb.StringProperty(required=True)
    manga_title = ndb.StringProperty(required=True)
    total_ratings = ndb.JsonProperty(required=False)
    average_ratings = ndb.FloatProperty(required=False)
    api_ratings=ndb.StringProperty(required = True)
    reccomendations_value = ndb.IntegerProperty(required=False)
    genre = ndb.StringProperty(required=False)
    reviews = ndb.JsonProperty(required=True)
    imgurl = ndb.StringProperty(required=True)
    synopsis = ndb.TextProperty(required = True)
    chapter = ndb.IntegerProperty(required = False)

class MangaUser(ndb.Model):
    email = ndb.StringProperty(required=True)
    username = ndb.StringProperty(required=True)
    friends_list = ndb.JsonProperty(required=False)
    groups = ndb.StringProperty(required=False)
    background_img = ndb.StringProperty(required=False)
    profile_img = ndb.TextProperty (required=False)
    user_recommendations = ndb.StringProperty(required=False)
    user_ratings = ndb.JsonProperty(required=True)
    user_reviews = ndb.JsonProperty(required=True)
    favorites = ndb.JsonProperty(required=False)#store image, img title, img id

    def followfriend(self, friend):
        self.friends_list[friend.username]=friend.key.id()

    def removefriend(self,friend):
        del self.friends_list[friend.username]

class Group(ndb.Model):
    chat = ndb.StringProperty(required=False)
    members = ndb.KeyProperty(MangaUser)
