from google.appengine.ext import db
from user import User
from helper import Jinja_helper


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
    subject = db.StringProperty(required=True)
    # define column content as text
    content = db.TextProperty(required=True)
    # define column created as datetime
    created = db.DateTimeProperty(auto_now_add=True)
    # define column last_modified as datetime
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self):
        # render text and replacing string new line to html break <br>
        self._render_text = self.content.replace('\n', '<br>')
        return Jinja_helper.render_str("post.html", p=self)
