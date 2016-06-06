#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Undacity FSWDN
# Project: MultiuserBlog.
# by Sergey Ryzhikov (sergey-inform@ya.ru)
# License: GPLv2
#
import sys,os
import jinja2
import webapp2
from webapp2_extras.routes import RedirectRoute, PathPrefixRoute
Route = webapp2.Route


# Template engine

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
		loader = jinja2.FileSystemLoader(template_dir),
		autoescape = True,
		)

jinja_env.globals['uri_for'] = webapp2.uri_for # to use uri_for() in templates

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


# URI Routing

app = webapp2.WSGIApplication([
	RedirectRoute('/', redirect_to='/blog/'),
	RedirectRoute('/blog/', 'handlers.BlogFrontpage', strict_slash=True, name='blog-frontpage'),
	PathPrefixRoute('/blog', [
        Route('/newpost', 'handlers.BlogNewpost', name='blog-newpost'),
        Route(r'/<post_id:\d+>', 'handlers.BlogPost', name='blog-post'),
        Route(r'/<post_id:\d+>/edit', 'handlers.BlogEdit', name='blog-edit'),
        Route(r'/<post_id:\d+>/delete', 'handlers.BlogDelete', name='blog-delete'),
        Route(r'/<post_id:\d+>/vote', 'handlers.BlogVote', name='blog-vote' ),
    ]),
    Route('/login', 'auth.LoginHandler'),
    Route('/logout', 'auth.LogoutHandler'),
    Route('/signup', 'auth.SignupHandler'),
    
], debug=True)
