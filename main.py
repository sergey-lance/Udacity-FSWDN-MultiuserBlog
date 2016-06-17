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
from webapp2_extras import auth
from webapp2_extras import sessions

## Template engine
# TODO: a better solution: https://webapp-improved.appspot.com/api/webapp2_extras/jinja2.html#webapp2_extras.jinja2.Jinja2

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
		params['user'] = self.user_info
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
		
	@webapp2.cached_property
	def auth(self):
		"""Shortcut to access the auth instance as a property."""
		return auth.get_auth()
		
	@webapp2.cached_property
	def user_info(self):
		"""Shortcut to access a subset of the user attributes that are stored
		in the session.
		The list of attributes to store in the session is specified in
			config['webapp2_extras.auth']['user_attributes'].
		:returns
			A dictionary with most user information
		"""
		return self.auth.get_user_by_session()
	
	@webapp2.cached_property
	def user(self):
		"""Shortcut to access the current logged in user.
		Unlike user_info, it fetches information from the persistence layer and
			returns an instance of the underlying model.
		:returns
			The instance of the user model associated to the logged in user.
		"""
		user_info = self.user_info
		if user_info:
			return self.user_model.get_by_id(user_info['user_id'])
		else:
			return None
	
	@webapp2.cached_property
	def user_model(self):
		"""Returns the implementation of the user model.
		It is consistent with config['webapp2_extras.auth']['user_model'], if set.
		"""    
		return self.auth.store.user_model

	@webapp2.cached_property
	def session(self):
		"""Shortcut to access the current session."""
		return self.session_store.get_session(backend="datastore")


	# this is needed for webapp2 sessions to work
	def dispatch(self):
		self.session_store = sessions.get_store(request=self.request)
		try:
			webapp2.RequestHandler.dispatch(self)
		finally:
			self.session_store.save_sessions(self.response)


## Application configuration

appconfig = {
	'webapp2_extras.auth': {
		'user_model': 'models.User',
		'user_attributes': ['name', 'avatar'] # will be cached in session (no access to storage)
	},
	'webapp2_extras.sessions': {
		'secret_key': 'BEBEBEChangeItOnProductionServerBEBEBE'
	}
}

## Routing
Route = webapp2.Route

app = webapp2.WSGIApplication([
	RedirectRoute('/', redirect_to='/blog/', name='home'),
	RedirectRoute('/blog/', 'handlers.BlogFrontpage', strict_slash=True, name='blog-frontpage'), #done
	PathPrefixRoute('/blog', [
		Route('/newpost', 'handlers.BlogNewpost', name='blog-newpost'), #done
		PathPrefixRoute(r'/<post_id:\d+/?>', [
				Route(r'', 'handlers.BlogOnePost', name='blog-onepost'), #done
				Route(r'/edit', 'handlers.BlogEdit', name='blog-edit'), #done
				#~ Route(r'/delete', 'handlers.BlogEdit', handler_method='delete', name='blog-delete'), #
				Route(r'/vote', 'handlers.BlogVote', name='blog-vote' ), #
				Route(r'/comment', 'comments.PostComment', name='post-comment' ), #
		]),
		PathPrefixRoute(r'/comments/<comment_id:\d+>', [
			Route(r'/edit', 'comments.EditComment', name='comment-edit'),
			Route(r'/delete', 'comments.DeleteComment', name='comment-delete'),
		]),
	]),
	Route('/login', 'auth.LoginHandler', name="login"), #done
	Route('/logout', 'auth.LogoutHandler', name="logout"), #done
	Route('/signup', 'auth.SignupHandler', name="signup"), #done
	Route('/welcome', 'handlers.WelcomeHandler', name="welcome"), #done
	
], debug=True, config = appconfig)
