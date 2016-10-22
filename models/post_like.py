from google.appengine.ext import db
from user import User
from post import Post


class PostLikes(db.Model):
    """
        class for posting like data to datastore
        in relaation with Post and User model
        that inherit from db.Model
        attribute :
            post,user
    """
    # define column post as ReferenceProperty of post.post_likes
    post = db.ReferenceProperty(Post,
                                collection_name='post_likes')
    # define column user as ReferenceProperty of user.user_likes
    user = db.ReferenceProperty(User,
                                collection_name='user_likes')
