from handler import Handler

class ErrorPage(Handler):
    """
        class for showing forbiden access
        function :
            get()
    """
    def get(self):
        # rendering page error.html
        self.render("error.html")
