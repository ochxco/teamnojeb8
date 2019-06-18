from google.appengine.ext import ndb

class Manga(ndb.Model):
    manga_id = ndb.StringProperty(required=True)
    total_ratings = ndb.FloatProperty(required=False)
    average_ratings = ndb.FloatProperty(required=False)
    reccomendations_value = ndb.IntegerProperty(required=False)
    genre = ndb.StringProperty(required=False)

class MangaUser(ndb.Model):
    email = ndb.StringProperty(required=True)
    username = ndb.StringProperty(required=True)
    friends_list = ndb.JsonProperty(required=False)
    groups = ndb.StringProperty(required=False)
    user_recommendations = ndb.StringProperty(required=False)
    user_ratings = ndb.JsonProperty(required=False)
    user_reviews = ndb.JsonProperty(required=False)

    def followfriend(self, friend):
        self.friends_list[friend.username]=friend.key.id()

    def removefriend(self,friend):
        del self.friends_list[friend.username]

class Group(ndb.Model):
    chat = ndb.StringProperty(required=False)
    members = ndb.KeyProperty(MangaUser)



