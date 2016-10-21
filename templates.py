import webapp2
import handlers
from google.appengine.ext import db

# app define each url segment with specific class
app = webapp2.WSGIApplication([
                               ('/signup',handlers.auth.SignUp),
                               ('/login',handlers.auth.Login),
                               ('/logout',handlers.auth.Logout),
                               ('/welcome',handlers.welcome.Welcome),
                               ('/error_401',handlers.error.ErrorPage),
                               ('/success',handlers.success.SuccessPage),
                               # Blog CRUD
                               ('/',handlers.post.ListBlog),
                               ('/([0-9]+)',handlers.post.GetBlog),
                               ('/newpost',handlers.post.PostBlog),
                               ('/editpost/([0-9]+)',handlers.post.EditBlog),
                               ('/deletepost/([0-9]+)',handlers.post.DeleteBlog),
                               # Blog comment CRUD
                               ('/newcomment/([0-9]+)',handlers.post_comment.PostCommentBlog),
                               ('/editcomment/([0-9]+)',handlers.post_comment.EditCommentBlog),
                               ('/deletecomment/([0-9]+)',handlers.post_comment.DeleteCommentBlog),
                               # Blog like
                               ('/like/([0-9]+)',handlers.post_like.BlogLike)
                                ],
                                debug=True)
