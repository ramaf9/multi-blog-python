import hashlib
import random

from string import letters
from google.appengine.ext import db


# authentication
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
