import models
from handler import Handler
from google.appengine.ext import db

################ START OF GLOBAL ####################################################

def blog_key(name="default"):
    return db.Key.from_path('blogs',name)

################ HANDLER CLASS #######################################################

class PostCommentBlog(Handler):
    """
        class for handling new user's
        comment on post
        function :
            post()
    """
    def __init__(self, *args, **kwargs):
        super(PostCommentBlog, self).__init__(*args, **kwargs)
        if not self.user.name:
            redirect('error_401')

    def post(self,blog_id):
        comment = self.request.get('comment')
        # check user's action new comment or edit comment
        key = db.Key.from_path('Post', int(blog_id), parent=blog_key())
        post = db.get(key)
        # insert new post comment to db
        p = models.PostComments(parent=blog_key(), post=post, user = self.user, comment = comment)
        p.put()

        # return to specified post where id = blog_id
        self.redirect('/%s' % str(blog_id))

class DeleteCommentBlog(Handler):
    """
        class for handle deleting user's
        comment on blog
        function :
            get()
    """
    def __init__(self, *args, **kwargs):
        super(DeleteCommentBlog, self).__init__(*args, **kwargs)
        if not self.user.name:
            redirect('error_401')

    def get(self,comment_id):
        p = models.PostComments.by_id(comment_id)
        # if it is user's post
        if p.user.name == self.user.name:
            # delete user's post
            p.delete()
            self.redirect('/')
        else:
            # show error
            self.redirect('error_401')

class EditCommentBlog(Handler):
    """
        class for handle edit user's
        comment on blog
        function :
            post()
    """
    def __init__(self, *args, **kwargs):
        super(EditCommentBlog, self).__init__(*args, **kwargs)
        if not self.user.name:
            redirect('error_401')

    def post(self,comment_id):
        comment = self.request.get('comment')
        key = db.Key.from_path('models.PostComments', int(comment_id), parent=blog_key())
        p = db.get(key)
        # check user's action new comment or edit comment
        if comment :
            # if it is user's post
            if p.user.name == self.user.name:
                # update user post
                p.comment = comment
                p.put()
            else:
                self.redirect('error_401')
        self.redirect('/%s' % str(p.post.key().id()))
        # return to specified post where id = blog_id
