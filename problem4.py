import webapp2
import re
import random
import string
import hashlib

from handler import Handler
from google.appengine.ext import db

class MainPage(Handler):
	def get(self):
		self.write("Problem Set 4")

class User(db.Model):
	username = db.StringProperty(required = True)
	hashpass = db.StringProperty(required = True)
	salt = db.StringProperty(required = True)
	email = db.StringProperty()

SECRET = string.letters

class Helper:
	@staticmethod
	def gen_salt():
		return ''.join(random.choice(string.letters) for x in xrange(10))

	@staticmethod
	def hash_password(un, pw, salt):
		return hashlib.sha256(un + pw + salt).hexdigest()

	@staticmethod
	def hash_cookie(user_id):
		return "%s|%s" % (user_id, hashlib.sha256(SECRET + user_id).hexdigest())

	@staticmethod
	def verify_cookie(cookie):
		user_id = cookie.split("|")[0]
		return Helper.hash_cookie(user_id) == cookie

	@staticmethod
	def user_from_cookie(cookie):
		user_id = cookie.split("|")[0]
		return User.get_by_id(int(user_id))

	@staticmethod
	def add_cookie(headers, user):
		user_id = user.key().id()
		cookie = Helper.hash_cookie(str(user_id))
		headers.add_header('Set-Cookie', "user_id=%s; Path=/" % cookie)


class SignupPage(Handler):
	def get(self):
		self.render_page()

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")

		username_error = password_error = verify_error = email_error = ""
		
		if not username:
			username_error = "Username needed"
		if not password:
			password_error = "Password needed"
		if verify != password:
			verify_error = "Password must match"
		if email and not re.match(r'\w+@\w+\.\w+', email):
			email_error = "Email not valid"

		if username_error or password_error or verify_error or email_error:
			self.render_page(username=username, username_error=username_error, 
				password_error=password_error, 
				verify_error=verify_error, 
				email=email, email_error=email_error)
		else:
			salt = Helper.gen_salt()
			hashpass = Helper.hash_password(username, password, salt)
			user = User(username=username, hashpass=hashpass, salt=salt, email=email)
			user.put()
			# set cookie
			Helper.add_cookie(self.response.headers, user)
			self.redirect('/welcome')

	def render_page(self, username="", username_error="", password_error="", verify_error="", email="", email_error=""):
		self.render("problem4-signup.html", 
			username=username, username_error=username_error, 
			password_error=password_error, 
			verify_error=verify_error, 
			email=email, email_error=email_error)

class WelcomePage(Handler):
	def get(self):
		cookie = self.request.cookies.get("user_id")
		if (cookie and Helper.verify_cookie(cookie)):
			user = Helper.user_from_cookie(cookie)
			self.render("problem4-welcome.html", username=user.username)
		else:
			self.redirect('/signup')

class LoginPage(Handler):
	def get(self):
		self.render("problem4-login.html")

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		user = User.gql("WHERE username=:1", username).get()
		if user:
			tryhash = Helper.hash_password(username, password, user.salt)
			if tryhash == user.hashpass:
				Helper.add_cookie(self.response.headers, user)
				self.redirect('/welcome')
			else:
				self.render("problem4-login.html", login_error="Wrong password")
		else:
			self.render("problem4-login.html", login_error="User not found")

class LogoutPage(Handler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', "user_id=; Path=/")
		self.redirect("/signup")

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/signup', SignupPage),
    ('/welcome', WelcomePage),
    ('/login', LoginPage),
    ('/logout', LogoutPage),
], debug=True)