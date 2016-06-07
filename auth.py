#!/usr/bin/env python
# -*- coding: utf-8 -*-


#https://github.com/abahgat/webapp2-user-accounts
#csrf http://stackoverflow.com/questions/8384729/is-there-any-available-solution-to-provide-xsrf-csrf-support-for-google-app-engi
#https://gist.github.com/jgeewax/2942374

from main import RequestHandler


class LoginHandler(RequestHandler):
	def get(self):
		self.render('login.html')

class LogoutHandler(RequestHandler):
	def get(self):
		self.redirect('/')
		
class SignupHandler(RequestHandler):
	def get(self):
		self.render('signup.html')
