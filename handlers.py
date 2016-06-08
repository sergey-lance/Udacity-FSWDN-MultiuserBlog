#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main import RequestHandler

from collections import namedtuple

from auth import user_required

Post = namedtuple('Post', ['title','content'])
post = Post(title="hehe", content='con')


# Request Handlers
class WelcomeHandler(RequestHandler):
	@user_required
	def get(self):
		self.render('welcome.html')

class BlogFrontpage(RequestHandler):
	def get(self):
		self.render('blog-frontpage.html')

class BlogNewpost(RequestHandler):
	@user_required
	def get(self):
		self.render('blog-edit.html')

class BlogPost(RequestHandler):
	def get(self, post_id):
		self.render('blog-post.html', post=post)
		
class BlogEdit(RequestHandler):
	#@owner_required
	def get(self, post_id):
		self.render('blog-edit.html', post=post)
		
class BlogDelete(RequestHandler):
	#owner_required
	def get(self, post_id):
		self.write("Delete %s" %post_id)
		
class BlogVote(RequestHandler):
	@user_required
	def get(self, post_id):
		self.write("Vote %s" %post_id)
			

