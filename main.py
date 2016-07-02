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

import hmac
import logging
try:
	from urlparse import urlparse #python2.7
except ImportError:
	from urllib.parse import urlparse #python3

CSRF_PARAM_NAME = 'token'

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
	prevent_embedding = True # prevent embedding the page in <iframe> on another sites 
	
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		params['user'] = self.user_info
		params['csrf_helpers'] = {
			'token': self.csrf_token,
			'gen_token': self.gen_csrf_token, #function
			'token_for': self.get_csrf_token_for, #function
			'uri_for': self.get_csrf_uri_for, #function
			}
		return render_str(template, **params)

	def render(self, template, **kw):
		if self.prevent_embedding:
			self.response.headers.add('X-Frame-Options', 'DENY')
			
		self.write(self.render_str(template, **kw))
		
	@webapp2.cached_property
	def auth(self):
		'''Shortcut to access the auth instance as a property.'''
		return auth.get_auth()
		
	@webapp2.cached_property
	def user_info(self):
		'''Shortcut to access a subset of the user attributes that are stored
		in the session.
		The list of attributes to store in the session is specified in
			config['webapp2_extras.auth']['user_attributes'].
		:returns
			A dictionary with most user information
		'''
		return self.auth.get_user_by_session()
	
	@webapp2.cached_property
	def user(self):
		'''Shortcut to access the current logged in user.
		Unlike user_info, it fetches information from the persistence layer and
			returns an instance of the underlying model.
		:returns
			The instance of the user model associated to the logged in user.
		'''
		user_info = self.user_info
		if user_info:
			return self.user_model.get_by_id(user_info['user_id'])
		else:
			return None
	
	@webapp2.cached_property
	def user_model(self):
		'''Returns the implementation of the user model.
		It is consistent with config['webapp2_extras.auth']['user_model'], if set.
		'''    
		return self.auth.store.user_model

	@webapp2.cached_property
	def session(self):
		'''Shortcut to access the current session.'''
		return self.session_store.get_session(backend="datastore")

	# this is needed for webapp2 sessions to work
	def dispatch(self):
		self.session_store = sessions.get_store(request=self.request)
		try:
			webapp2.RequestHandler.dispatch(self)
		finally:
			self.session_store.save_sessions(self.response)
	
	
# CSRF handlers	
	def gen_csrf_token(self, uri=None):
		''' Generate a token to prevent CSRF attacks. 
			Token is unique for user session and URI:
			  token = hash(session.token + rquest.path)
			
			uri: to generate token for another URI 
		'''
		if not self.user_info: # no user session...
			return None # so csrf make no sense
		
		if uri is None:
			uri = self.request.path
		else:
			uri = urlparse(uri).path
		
		secret = self.user_info['token'] + uri
		token = hmac.new(
					key=bytearray(secret, 'utf-8'),
					# digestmod=hashlib.sha256
				).hexdigest()
			
		return token
			
	def check_csrf_token(self, token):
		if self.csrf_token == token \
			or self.csrf_token is None: # nothing to match:
				return True
		return False
	
	@property
	def csrf_token(self):
		''' Get CSRF token as a request property.
		'''
		return self.gen_csrf_token(self.request.path)

	def get_csrf_token_for(self, route_name, *a, **kva):
		''' Generate token for specified route.
		'''
		uri = webapp2.uri_for(route_name, *a, **kva)
		uri_path = urlparse(uri).path	# the same as request.path
		return self.gen_csrf_token(uri = uri_path)
		
	def get_csrf_uri_for(self, route_name, *a, **kva ):
		''' A handy function to generate csrf-aware URI's like /bebe?param=1&token=ab12cd34...
		'''
		token = self.get_csrf_token_for(route_name, **kva)
		kva[CSRF_PARAM_NAME] = token
		return webapp2.uri_for(route_name, *a, **kva)


def csrf_check(handler):
	''' Decorator for CSRF token check.
		
		Look for parameter with name 'CSRF_PARAM_NAME'
		in POST for posts and in GET for other request types.
		Aborts request if token is not valid.
	'''
	def _check_csrf_token(self, *args, **kwargs):
		req = self.request
		try:
			if req.method == 'POST':
				token = self.request.POST[CSRF_PARAM_NAME]
			else:
				token = self.request.GET[CSRF_PARAM_NAME]
		except KeyError:
			self.abort(401, explanation='CSRF token required.')
			
		if self.check_csrf_token(token):
			return handler(self, *args, **kwargs)
		else:
			self.abort(401, explanation='CSRF token doesn\'t match.')

	return _check_csrf_token
	
	
## Application configuration

appconfig = {
	'webapp2_extras.auth': {
		'user_model': 'models.User',
		'user_attributes': ['name', 'avatar'] # will be cached in session (no access to storage)
	},
	'webapp2_extras.sessions': {
		'secret_key': 'BEBEBEChangeItOnProductionServerBEBEBE',
		'cookie_args': {'httponly': True}, # enforce session cookies not to be accessible by JS
	}
}

## Routing
Route = webapp2.Route

app = webapp2.WSGIApplication([
	RedirectRoute('/', redirect_to='/blog/', name='home'),
	RedirectRoute('/blog/', 'handlers.BlogFrontpage', strict_slash=True, name='blog-frontpage'), #done
	PathPrefixRoute('/blog', [
		Route('/newpost', 'handlers.BlogNewpost', name='blog-newpost'), #done
		PathPrefixRoute(r'/<post_id:\d+>', [
				Route(r'', 'handlers.BlogOnePost', name='blog-onepost'), #done
				Route(r'/edit', 'handlers.BlogEdit', name='blog-edit'), #done
				Route(r'/delete', 'handlers.BlogDelete', name='blog-delete'), #done
				Route(r'/like', 'handlers.BlogLike', name='blog-like' ), #
				Route(r'/comment', 'handlers.PostComment', name='blog-comment' ), #done
				PathPrefixRoute(r'/comments/<comment_id:\d+>', [ #done
					Route(r'/edit', 'handlers.EditComment', name='comment-edit'), #done
					Route(r'/delete', 'handlers.DeleteComment', name='comment-delete'), #done
				]),
		]),
	]),
	Route('/login', 'auth.LoginHandler', name="login"), #done
	Route('/logout', 'auth.LogoutHandler', name="logout"), #done
	Route('/signup', 'auth.SignupHandler', name="signup"), #done
	Route('/welcome', 'handlers.WelcomeHandler', name="welcome"), #done
	
], debug=True, config = appconfig)
