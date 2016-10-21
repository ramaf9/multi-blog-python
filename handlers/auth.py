import re
import models
from handler import Handler
from google.appengine.ext import db

################ START OF GLOBAL ####################################################

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

################ HANDLER CLASS #######################################################

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
            u = models.User.by_name(username)
            # check if users already exist
            if u:
                msg = 'User already exist'
                self.render('sign_up.html', error_username = msg)
            else:
                # inserting new user
                u = models.User.register(username, password, email)
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
        u = models.User.login(username,password)
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
    def __init__(self, *args, **kwargs):
        super(Logout, self).__init__(*args, **kwargs)
        if not self.user.name:
            redirect('error_401')

    def get(self):
        # call parent function to logout
        self.logout()
        self.redirect("/")
