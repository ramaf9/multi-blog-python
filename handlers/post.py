import models
from handler import Handler
from google.appengine.ext import db

################ START OF GLOBAL ####################################################

def blog_key(name="default"):
    return db.Key.from_path('blogs',name)

################ HANDLER CLASS #######################################################

class ListBlog(Handler):
    """
        class for handling front page showing
        all post
        function :
            get()
    """
    def get(self):
        # get request from key sort
        sort = self.request.get('sort')
        if not sort:
            sort = "desc"
        # retrieve anything from post table with sql query like
        posts = db.GqlQuery("select * from Post order by created %s limit 10" %sort)
        self.render("front.html", posts = posts,sort = sort)

class GetBlog(Handler):
    """
        class for show specified
        blog with blog id and posting like
        function :
            get()
    """
    def get(self,blog_id):
        # get post with id = blog_id in url segment
        key = db.Key.from_path('Post', int(blog_id), parent=blog_key())
        post = db.get(key)
        like = False
        # get all post_likes value
        for p in post.post_likes:
            # if users already like
            if self.user.name == p.user.name:
                like=True
                break

        # if post not exist with current key
        if not post:
            # 404 page not found
            self.error(404)
            return
        c_id = self.request.get('c_id')
        # if users wants to edit
        if c_id:
            key = db.Key.from_path('PostComments', int(c_id), parent=blog_key())
            c_id = db.get(key)
            if c_id.user.name == self.user.name:
                c_id = c_id.key().id()

        # show permalink html
        self.render("permalink.html", post = post, likes = like , c_id = c_id)

class PostBlog(Handler):
    """
        class for handling new post and edit post
        function :
            get()
            post()
    """
    def __init__(self, *args, **kwargs):
        super(PostBlog, self).__init__(*args, **kwargs)
        if not self.user.name:
            redirect('error_401')

    def get(self):
        # show new post
        self.render("newpost.html")

    def post(self):
        # retrieve request from post
        subject = self.request.get('subject')
        content = self.request.get('content')

        # check if its have value
        if subject and content:
            # inserting new post
            post = models.Post(parent=blog_key(), user=self.user, subject = subject, content = content)
            post.put()
            # redirect to recent post blog
            self.redirect('/%s' % str(post.key().id()))
        else:
            # set error message
            error = "subject and content, please"
            # show newpost html with params
            self.render("newpost.html", subject=subject, content=content, error=error)

class EditBlog(Handler):
    """
        class for handle user's blog edit
        function :
            get()
            post()
    """
    def __init__(self, *args, **kwargs):
        super(EditBlog, self).__init__(*args, **kwargs)
        if not self.user.name:
            redirect('error_401')

    def get(self,blog_id):
        key = db.Key.from_path('Post', int(blog_id), parent=blog_key())
        post = db.get(key)
        self.render("editpost.html", subject=post.subject, content=post.content)

    def post(self,blog_id):
        # retrieve request from post
        subject = self.request.get('subject')
        content = self.request.get('content')

        # check if its have value
        if subject and content:
            key = db.Key.from_path('Post', int(blog_id), parent=blog_key())
            post = db.get(key)
            # check if user's post
            if self.user.name == post.user.name:
                # update post
                post.content = content
                post.subject = subject
                post.put()
            else:
                # show error
                self.redirect('error_401')
            # redirect to recent post blog
            self.redirect('/%s' % str(post.key().id()))
        else:
            # set error message
            error = "subject and content, please"
            # show newpost html with params
            self.render("editpost.html", subject=subject, content=content, error=error)

class DeleteBlog(Handler):
    """
        class for handle delete user's blog
        function :
            get()
    """
    def __init__(self, *args, **kwargs):
        super(DeleteBlog, self).__init__(*args, **kwargs)
        if not self.user.name:
            redirect('error_401')

    def get(self,blog_id):
        # get post from db
        key = db.Key.from_path('Post', int(blog_id), parent=blog_key())
        post = db.get(key)
        # check if blog_id is user's post
        if post.user.name == self.user.name:
            # delete current post
            delete = post.delete()
            self.redirect('success')
        else:
            # show error
            self.redirect('error_401')
