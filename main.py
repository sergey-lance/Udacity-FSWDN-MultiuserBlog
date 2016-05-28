#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
""" Undacity FSWDN, Homework for MultiuserBlog project.
"""
import sys,os

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

app = webapp2.WSGIApplication([
	('/', Rot13Handler),
	('/rot13', Rot13Handler),
], debug=True)


		


