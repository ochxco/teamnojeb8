from google.appengine.ext import ndb

class Manga(ndb.Model):
    manga_id = ndb.StringProperty(required=True)
    manga_title = ndb.StringProperty(required=True)
    total_ratings = ndb.JsonProperty(required=False)
    average_ratings = ndb.FloatProperty(required=False)
    reccomendations_value = ndb.IntegerProperty(required=False)
    genre = ndb.StringProperty(required=False)
    reviews = ndb.JsonProperty(required=True)

class MangaUser(ndb.Model):
    email = ndb.StringProperty(required=True)
    username = ndb.StringProperty(required=True)
    friends_list = ndb.StringProperty(required=False)
    groups = ndb.StringProperty(required=False)
    user_recommendations = ndb.StringProperty(required=False)
    user_ratings = ndb.JsonProperty(required=True)
    user_reviews = ndb.JsonProperty(required=True)

class Group(ndb.Model):
    chat = ndb.StringProperty(required=False)
    members = ndb.KeyProperty(MangaUser)
