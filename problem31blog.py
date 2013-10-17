import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Post(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
	def get(self):
		posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
		self.render("blog-index.html", posts=posts)

class NewPostPage(Handler):
	def get(self):
		self.render("blog-form.html", subject="", content="", error="")

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")

		if subject and content:
			p = Post(subject=subject, content=content)
			key = p.put()
			self.redirect("/blog/%d" % key.id())
		else:
			error = "subject and content needed"
			self.render("blog-form.html", subject=subject, content=content, error=error)

class DetailPage(Handler):
	def get(self, id):
		p = Post.get_by_id(int(id))
		self.render("blog-detail.html", p=p)

app = webapp2.WSGIApplication([
    ('/blog/?', MainPage),
    ('/blog/newpost', NewPostPage),
    ('/blog/(\d+)', DetailPage),
], debug=True)
