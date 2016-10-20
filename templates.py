import os
import webapp2
import jinja2
import re
import random
import hashlib
import hmac

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

################ START OF GLOBAL ####################################################

#global variable
secret = "abcd"
letters = "123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ"
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PW_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

# global function
def valid_username(username):
    return USER_RE.match(username)
def valid_pw(username):
    return PW_RE.match(username)
def valid_email(username):
    return EMAIL_RE.match(username)
def blog_key(name="default"):
    return db.Key.from_path('blogs',name)
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# authentication methods
def make_secure_val(val): # generate hmac for cookies value
    return '%s|%s' %(val,hmac.new(secret,val).hexdigest())
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val
def make_salt(length = 5): # generate random string
    return ''.join(random.choice(letters) for x in xrange(length))
def make_pw_hash(name,pw,salt = None): # hashing pw with user+pw+salt
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt,h)
def login_valid_pw(name,password,h): # checking hash
    salt = h.split(',')[0]
    return h==make_pw_hash(name,password,salt)
def users_key(group = "default"): # initiate users group
    return db.Key.from_path('users',group)


################ END OF GLOBAL ######################################################

class Handler(webapp2.RequestHandler):
    """
        parent class for each controller
        with function :
            write()
            render_str()
            render()
            set_secure_cookie()
            read_secure_cookie()
            login()
            logout()
            initialize()
    """
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)
    # rendering string from html template
    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)
    # rendering from html template
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    # set cookie with encryoted value
    def set_secure_cookie(self,name,val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' %(name,cookie_val))
    # read encrypted cookie
    def read_secure_cookie(self,name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)
    # set user in cookie
    def login(self,user):
        self.set_secure_cookie('user_id',str(user.key().id()))
    # set user cookie to null
    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=;Path=/')
    # check user every requested page
    def initialize(self,*a,**kw):
        webapp2.RequestHandler.initialize(self,*a,**kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

################ MODEL CLASSES ######################################################

class User(db.Model):
    """
        class for saving user authentication
        in datastore
        attribute :
            name,pw_hash,email
        function :
            by_id()
            by_name()
            register()
            login()
    """
    # define column in User
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    # define classmethods
    @classmethod
    def by_id(cls, uid): # search user by id
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name): # get all user by name
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and login_valid_pw(name, pw, u.pw_hash):
            return u


class Post(db.Model):
    """
        class for posting data to datastore
        that inherit from db.Model
        attribute :
            user,subject,content,created,
            last_modified
        function :
            render()
    """
    user = db.ReferenceProperty(User,
                                collection_name='user_post')
    # define column subject as string
    subject = db.StringProperty(required = True)
    # define column content as text
    content = db.TextProperty(required = True)
    # define column created as datetime
    created = db.DateTimeProperty(auto_now_add = True)
    # define column last_modified as datetime
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        # render text and replacing string new line to html break <br>
        self._render_text = self.content.replace('\n','<br>')
        return render_str("post.html", p = self)

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

class PostLike(db.Model):
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
    # comments = db.StringProperty()


################ END OF MODEL CLASSES ################################################

class Error(Handler):
    """
        class for showing forbiden access
        function :
            get()
    """
    def get(self):
        # rendering page error.html
        self.render("error.html")

class MainPage(Handler):
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
        c_id = self.request.get('id')
        # if users wants to edit
        if c_id:
            c_id = int(c_id)
        # show permalink html
        self.render("permalink.html", post = post, likes = like , c_id = c_id)

    def post(self,blog_id):
        # get post with id = blog_id in url segment
        key = db.Key.from_path('Post', int(blog_id), parent=blog_key())
        post = db.get(key)
        action = self.request.get('action')
        like = False
        # check if user already liked
        for p in post.post_likes:
            if self.user.name == p.user.name:
                like=True
                break
        # if user request post_like
        if action == 'post_like':
            if not like:
                # insert new like
                p = PostLike(parent=blog_key(), post=post, user = self.user)
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
                    self.redirect('error')
        self.redirect('/%s' % str(post.key().id()))

class CommentBlog(Handler):
    """
        class for handling users comment on post
        function :
            get()
            post()
    """
    def get(self,comment_id):
        action = self.request.get('action')
        # check if users action is delete_comment
        if action == "delete_comment":
            p = PostComments.by_id(comment_id)
            # if it is user's post
            if p.user.name == self.user.name:
                # delete user's post
                p.delete()
                self.redirect('/')
            else:
                # show error
                self.redirect('error')
        else:
            self.redirect('/')

    def post(self,blog_id):
        action = self.request.get('action')
        comment = self.request.get('comment')
        # check user's action new comment or edit comment
        if action == 'post_comment':
            key = db.Key.from_path('Post', int(blog_id), parent=blog_key())
            post = db.get(key)
            # insert new post comment to db
            p = PostComments(parent=blog_key(), post=post, user = self.user, comment = comment)
            p.put()

        elif action == "edit_comment":
            comment_id = self.request.get('comment_id')
            key = db.Key.from_path('PostComments', int(comment_id), parent=blog_key())
            p = db.get(key)
            # if it is user's post
            if p.user.name == self.user.name:
                # update user post
                p.comment = comment
                p.put()
            else:
                self.redirect('error')
        # return to specified post where id = blog_id
        self.redirect('/%s' % str(blog_id))


class PostBlog(Handler):
    """
        class for handling new post and edit post
        function :
            get()
            post()
    """
    def get(self):
        # show newpost html
        blog_id = self.request.get('id')
        action = self.request.get('action')
        # check if it contains id or not
        if not blog_id:
            # show new post
            self.render("newpost.html")
        elif blog_id:
            # get post from db
            key = db.Key.from_path('Post', int(blog_id), parent=blog_key())
            post = db.get(key)
            # check if blog_id is user's post
            if post.user.name == self.user.name:
                if action == "edit_blog":
                    # show edit post page
                    self.render("newpost.html", subject = post.subject,
                                content = post.content,
                                action = action)
                elif action == "delete_blog":
                    # delete current post
                    delete = post.delete()
                    self.redirect('')
            else:
                # show error
                self.redirect('error')

    def post(self):
        # retrieve request from post
        subject = self.request.get('subject')
        content = self.request.get('content')

        # check if its have value
        if subject and content:
            # check action value
            action = self.request.get('action')
            if action == "edit_blog":
                blog_id = self.request.get('id')
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
                    self.redirect('error')

            else:
                # inserting new post
                post = Post(parent=blog_key(), user=self.user, subject = subject, content = content)
                post.put()
            # redirect to recent post blog
            self.redirect('/%s' % str(post.key().id()))
        else:
            # set error message
            error = "subject and content, please"
            # show newpost html with params
            self.render("newpost.html", subject=subject, content=content, error=error)


class SignUp(Handler):
    """
        class that handle for user registration
        function :
            get()
            post()
    """
    def get(self):
        # show sign up page
        self.render("sign_up.html")
    def post(self):
        # initial wihtout error
        have_error = False;
        username = self.request.get("username")
        password = self.request.get("password")
        m_password = self.request.get("verify")
        email = self.request.get("email")

        params = dict(username = username,
                      email = email)
        # check if users input are all valid
        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True
        if not valid_pw(password):
            params['error_password'] = "That's not a valid password."
            have_error = True
        elif m_password != password :
            params['error_m_password'] = "Your password didn't match."
            have_error = True
        if not valid_email(email) and email:
            params['error_email'] = "That's not a valid email."
            have_error = True
        # check if its have error
        if have_error:
            # show page with error
            self.render("sign_up.html", **params)
        else:
            u = User.by_name(username)
            # check if users already exist
            if u:
                msg = 'User already exist'
                self.render('sign_up.html', error_username = msg)
            else:
                # inserting new user
                u = User.register(username, password, email)
                u.put()
                # user's login
                self.login(u)
                # redirect to welcome page
                self.redirect("/welcome?username="+username)

class Login(Handler):
    """
        class that handle user login
        function :
            get()
            post()
    """
    def get(self):
        # show login page
        self.render('login_form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        u = User.login(username,password)
        # check user username and password
        if u:
            # data valid
            self.login(u)
            # redirect to welcome
            self.redirect("/welcome?username="+ u.name)
        else:
            # set error message
            msg = 'Invalid login'
            # show page with error
            self.render('login_form.html', error = msg)

class Logout(Handler):
    """
        class for handling user's logout
    """
    def get(self):
        # call parent function to logout
        self.logout()
        self.redirect("/")


class Welcome(Handler):
    """
        class for handle user's greeting
        function :
            get()
    """
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username=self.user.name)
        else:
            self.redirect('/signup')

# app define each url segment with specific class
app = webapp2.WSGIApplication([('/',MainPage),
                               ('/signup',SignUp),
                               ('/login',Login),
                               ('/logout',Logout),
                               ('/welcome',Welcome),
                               ('/error',Error),
                               ('/([0-9]+)',GetBlog),
                               ('/newpost',PostBlog),
                               ('/commentblog/([0-9]+)',CommentBlog)
                                ],
                                debug=True)
