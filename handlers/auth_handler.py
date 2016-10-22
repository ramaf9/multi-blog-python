import webapp2
import models
import hmac
from helper import Jinja_helper

# START GLOBAL VARIABLE

secret = "abcd"
# authentication methods


def make_secure_val(val):  # generate hmac for cookies value
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


# STAR HANDLER CLASS


class AuthHandler(webapp2.RequestHandler):
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
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # rendering string from html template
    def render_str(self, template, **params):
        params['user'] = self.user
        return Jinja_helper.render_str(template, **params)

    # rendering from html template
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    # set cookie with encryoted value
    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    # read encrypted cookie
    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    # set user in cookie
    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    # set user cookie to null
    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=;Path=/')

    # check user state
    def dispatch(self):
        if self.user:
            # Parent class will call the method to be dispatched
            # -- get() or post() or etc.
            super(Handler, self).dispatch()
        else:
            return self.redirect('/login')
            # self.abort(403)

    # check user every requested page
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and models.User.by_id(int(uid))
