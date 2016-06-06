#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main import RequestHandler

# Request Handlers
class WelcomeHandler(RequestHandler):
	def get(self):
		username = self.request.get('username')
		self.render('welcome.html', username = username)

class BlogFrontpage(RequestHandler):
	def get(self):
		self.write("Blog" )

class BlogNewpost(RequestHandler):
	def get(self):
		self.write("New")

class BlogPost(RequestHandler):
	def get(self, post_id):
		self.write("Post %s" %post_id)
		
class BlogEdit(RequestHandler):
	def get(self, post_id):
		self.write("Edit %s" %post_id)
		
class BlogDelete(RequestHandler):
	def get(self, post_id):
		self.write("Delete %s" %post_id)
		
class BlogVote(RequestHandler):
	def get(self, post_id):
		self.write("Vote %s" %post_id)
			

