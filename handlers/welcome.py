from auth_handler import AuthHandler
import models


class Welcome(AuthHandler):
    """
        class for handle user's greeting
        function :
            get()
    """

    def get(self):
        username = self.user.name
        if username:
            self.render('welcome.html', username=username)
        else:
            self.redirect('/signup')
