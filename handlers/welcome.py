from handler import Handler
import models

class Welcome(Handler):
    """
        class for handle user's greeting
        function :
            get()
    """
    def __init__(self, *args, **kwargs):
        super(Welcome, self).__init__(*args, **kwargs)
        if not self.user:
            self.redirect('/error_401')

    def get(self):
        username = self.user.name
        if username:
            self.render('welcome.html', username=username)
        else:
            self.redirect('/signup')
