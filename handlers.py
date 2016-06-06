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
		self.write("Blog")

class BlogNewpost(RequestHandler):
	def get(self):
		self.write("New")

class BlogPost(RequestHandler):
	def get(self, post_id):
		self.write("Post")
		
class BlogEdit(RequestHandler):
	def get(self, post_id):
		self.write("Edit")
		
class BlogDelete(RequestHandler):
	def get(self, post_id):
		self.write("Delete")
		
class BlogVote(RequestHandler):
	def get(self, post_id):
		self.write("Vote")
			

