from google.appengine.ext import ndb

class Manga(ndb.model):
    manga_id = ndb.StringProperty(required=True)
    total_ratings = ndb.FloatProperty(required=False)
    average_ratings = ndb.FloatProperty(required=False)
    reccomendations_value = ndb.IntegerProperty(required=False)
    genre = ndb.StringProperty(required=False)

class Friends(ndb.model):
    user = ndb.StringProperty(required=True)
    friends_list = ndb.StringProperty(required=False)
    groups = ndb.StringProperty(required=False)
