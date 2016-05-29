#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
""" Undacity FSWDN, Homework for MultiuserBlog project.
"""
import sys,os,re

import webapp2
import jinja2

# Template engine
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
		loader = jinja2.FileSystemLoader(template_dir),
		autoescape = True,
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

app = webapp2.WSGIApplication([
	('/', SignupHandler),
	('/signup', SignupHandler),
	('/rot13', Rot13Handler),
	('/welcome', WelcomeHandler),
], debug=True)


		


