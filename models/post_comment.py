from google.appengine.ext import db
from user import User
from post import Post

class PostComments(db.Model):
    """
        class for posting comment to datastore
        in relation with Post and User model
        that inherit from db.Model
        attribute :
            user,post,comment
        function :
            by_id()
            by_user()
            by_post()
    """
    # define column post as ReferenceProperty of post.post_comments
    post = db.ReferenceProperty(Post,
                                collection_name='post_comments')
    # define column user as ReferenceProperty of user.user_comments
    user = db.ReferenceProperty(User,
                                collection_name='user_comments')
    comment = db.TextProperty()
    @classmethod
    def by_id(cls, uid): # search user by id
        return PostComments.get_by_id(uid)

    @classmethod
    def by_user(cls, user): # get all user by name
        u = PostComments.all().filter('user =', user).get()
        return u

    @classmethod
    def by_post(cls, post): # get all user by name
        u = PostComments.all().filter('post =', post).get()
        return u
