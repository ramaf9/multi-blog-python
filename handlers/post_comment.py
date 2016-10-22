import models
from auth_handler import AuthHandler
from google.appengine.ext import db

# START GLOBAL


def blog_key(name="default"):
    return db.Key.from_path('blogs', name)

# START HANDLER CLASS


class PostCommentBlog(AuthHandler):
    """
        class for handling new user's
        comment on post
        function :
            post()
    """

    def post(self, blog_id):
        comment = self.request.get('comment')
        # check user's action new comment or edit comment
        key = db.Key.from_path('Post', int(blog_id), parent=blog_key())
        post = db.get(key)
        # insert new post comment to db
        p = models.PostComments(
            parent=blog_key(), post=post, user=self.user, comment=comment)
        p.put()

        # return to specified post where id = blog_id
        self.redirect('/%s' % str(blog_id))


class DeleteCommentBlog(AuthHandler):
    """
        class for handle deleting user's
        comment on blog
        function :
            get()
    """

    def get(self, comment_id):
        key = db.Key.from_path('PostComments', int(
            comment_id), parent=blog_key())
        p = db.get(key)
        # if it is user's post
        if p.user.name == self.user.name:
            # delete user's post
            p.delete()
            self.redirect('/%s' % p.post.key().id())
        else:
            # show error
            self.redirect('error_401')


class EditCommentBlog(AuthHandler):
    """
        class for handle edit user's
        comment on blog
        function :
            post()
    """

    def post(self, comment_id):
        comment = self.request.get('comment')
        key = db.Key.from_path('PostComments', int(
            comment_id), parent=blog_key())
        p = db.get(key)
        # check user's action new comment or edit comment
        if comment:
            # if it is user's post
            if p.user.name == self.user.name:
                # update user post
                p.comment = comment
                p.put()
            else:
                self.redirect('error_401')
        self.redirect('/%s' % str(p.post.key().id()))
        # return to specified post where id = blog_id
