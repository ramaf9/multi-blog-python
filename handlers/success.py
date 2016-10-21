from handler import Handler

class SuccessPage(Handler):
    """
        class for showing forbiden access
        function :
            get()
    """
    def get(self):
        # rendering page error.html
        self.render("success.html")
