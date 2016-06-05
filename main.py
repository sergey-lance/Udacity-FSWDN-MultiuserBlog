#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
""" Undacity FSWDN, Homework for MultiuserBlog project.
"""
import sys,os,re

import webapp2
import jinja2

from google.appengine.ext import db
from lxml.html.clean import Cleaner

# Template engine
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
		loader = jinja2.FileSystemLoader(template_dir),
		autoescape = True,
		)

# Html cleaner
ALLOW_TAGS = ['a', 'img', 'abbr', 'acronym', 'q',
		'b', 'i', 'u', 'em', 's', 'small', 'sub', 'sup',
		'br', 'p',
		'pre', 'code', 'del', 'ins',
		'li', 'ol', 'ul', 'dl', 'dd', 'dt',
		]
		
html_cleaner = Cleaner(
		safe_attrs_only = True,
		add_nofollow=True,
		allow_tags = ALLOW_TAGS,
		remove_unknown_tags = False, #need this
		)

def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params) 

class RequestHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))


# Handlers
class Rot13Handler(RequestHandler):
	def get(self):
		self.render('rot13-form.html')
	
	def post(self):
		text = self.request.get('text')
		rot13=""
		if text:
			rot13 = text.encode('rot13', errors='ignore') #ignore unicode chars
			
		self.render('rot13-form.html', text = rot13)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

def valid_username(username):
	return username and USER_RE.match(username)

def valid_password(password):
	return password and PASS_RE.match(password)

def valid_email(email):
	return (email=="") or EMAIL_RE.match(email)

class SignupHandler(RequestHandler):
	def get(self):
		self.render('signup-form.html')
	
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		verify = self.request.get('verify')
		email = self.request.get('email')
		
		params = dict(username = username,
				email = email)
				
		err_params = {}
		
		if not valid_email(email):
			err_params['err_email'] = 'Email is not valid.'
		
		if not valid_username(username):
			err_params['err_username'] = 'Username is not valid.'
		
		if not valid_password(password):
			err_params['err_password'] = 'Password is not valid.'
			
		if password != verify:
			err_params['err_verify'] = 'Passwords doesn\'t match.'
		
		if err_params:
			self.render('signup-form.html',  **dict(params, **err_params) 	)
		else:
			self.redirect('/welcome?username=%s' % username)
		
class WelcomeHandler(RequestHandler):
	def get(self):
		username = self.request.get('username')
		if valid_username(username):
			self.render('welcome.html', username = username)
		else:
			self.redirect('/signup')

### Blog
def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)

class Post(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	
	def render(self):
		self._render_text = self.content.replace('\n', '<br>')
		return render_str("post.html", p = self)

class BlogFrontpage(RequestHandler):
	def get(self):
		posts = db.GqlQuery("select * from Post order by created desc limit 10")
		self.render('blog-frontpage.html', posts = posts)

class BlogPost(RequestHandler):
	def get(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)

		if not post:
			self.error(404)
			return

		self.render("blog-post.html", post = post)

class BlogNewpost(RequestHandler):
	def get(self):
		self.render("blog-newpost.html")
	
	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content')
		content = html_cleaner.clean_html(content)

		if subject and content:
			p = Post(parent = blog_key(), subject = subject, content = content)
			p.put()
			self.redirect('/blog/%s' % str(p.key().id()))
		else:
			error = "subject and content, please!"
			self.render("blog-newpost.html", subject=subject, content=content, error=error)

app = webapp2.WSGIApplication([
	('/', SignupHandler),
	('/signup', SignupHandler),
	('/rot13', Rot13Handler),
	('/welcome', WelcomeHandler),
	('/blog/?', BlogFrontpage),
	('/blog/([0-9]+)', BlogPost),
	('/blog/newpost', BlogNewpost),
], debug=True)


		


