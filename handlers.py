#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main import RequestHandler

from collections import namedtuple

Post = namedtuple('Post', ['title','content'])
post = Post(title="hehe", content='con')

# Request Handlers
class WelcomeHandler(RequestHandler):
	def get(self):
		username = self.request.get('username')
		self.render('welcome.html', username = username)

class BlogFrontpage(RequestHandler):
	def get(self):
		self.render('blog-frontpage.html')

class BlogNewpost(RequestHandler):
	def get(self):
		self.render('blog-edit.html')

class BlogPost(RequestHandler):
	def get(self, post_id):
		self.render('blog-post.html', post=post)
		
class BlogEdit(RequestHandler):
	def get(self, post_id):
		self.render('blog-edit.html', post=post)
		
class BlogDelete(RequestHandler):
	def get(self, post_id):
		self.write("Delete %s" %post_id)
		
class BlogVote(RequestHandler):
	def get(self, post_id):
		self.write("Vote %s" %post_id)
			

