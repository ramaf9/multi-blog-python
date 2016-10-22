import models
from auth_handler import AuthHandler
from google.appengine.ext import db

################ START OF GLOBAL #########################################


def blog_key(name="default"):
    return db.Key.from_path('blogs', name)

################ HANDLER CLASS ###########################################


class BlogLike(AuthHandler):
    """
        class for handle user's like and unlike
        on blog
        function :
            get()
    """

    def get(self, blog_id):
        # get blog with id = blog_id in url segment
        key = db.Key.from_path('Post', int(blog_id), parent=blog_key())
        post = db.get(key)
        action = self.request.get('action')
        like = False
        # check if user already liked
        for p in post.post_likes:
            if self.user.name == p.user.name:
                like = True
                break
        # if user not liked
        if not like:
            # insert new like
            p = models.PostLikes(parent=blog_key(), post=post, user=self.user)
            p.put()
        else:
            success = False
            # delete users like
            for p in post.post_likes:
                if self.user.name == p.user.name:
                    p.delete()
                    success = True
            # if not authorized show error
            if not success:
                self.redirect('error_401')
        self.redirect('/%s' % str(post.key().id()))
