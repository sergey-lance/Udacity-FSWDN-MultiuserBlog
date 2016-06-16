#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main import RequestHandler
from google.appengine.ext import ndb
from lxml.html.clean import Cleaner

from auth import user_required
from models import Post, Comment, User


# HTML cleaner
ALLOW_TAGS = ['a', 'li', 'ol', 'ul', 'em', 'strong', 'del', 'ins', 'br', 'p', #symantic tags
		'abbr', 'acronym','sub', 'sup', 'pre', 'code', #some harmless tags
		]
		
_html_cleaner = Cleaner(
		safe_attrs_only = True,
		add_nofollow=True,
		allow_tags = ALLOW_TAGS,
		remove_unknown_tags = False, #need this
		)

# Request Handlers
class WelcomeHandler(RequestHandler):
	@user_required
	def get(self):
		self.render('welcome.html')

class BlogFrontpage(RequestHandler):
	def get(self):
		# Posts
		posts = Post.query().order(-Post.created).fetch() #TODO: pagination
		
		# Users
		user_keys = set((p.author for p in posts)) 
		users = ndb.get_multi(user_keys) #fetch user records at once to save PRCs.
		users_data = (u.to_dict(include=['name', 'avatar']) for u in users)
		users_dict = dict(zip(user_keys, users_data))
		
		self.render('blog-frontpage.html', posts=posts, users_dict=users_dict)


def _verify_post_params(request):
	''' 
	Get and clean up parameters from request.
	Returns a tuple: (is_ok, template parameters)
	'''
	is_ok = True
	
	title = request.get('title')
	content = request.get('content-html')
	if content:
		content = _html_cleaner.clean_html(content)
	
	params = dict(title=title, content=content)
	
	if not title:
		is_ok = False
		params['err_title'] = 'Post should have a title.'
		
	if not content:
		is_ok = False
		params['error'] = 'Post should have a content.'
	
	return is_ok, params

def _user_is_author(user, post):
	if user.key == post.author:
		return True
	else:
		return False

class BlogNewpost(RequestHandler):
	@user_required
	def get(self):
		self._serve()
	
	@user_required
	def post(self):
		is_ok, params = _verify_post_params(self.request)
		
		post = Post( content = params['content'],
				title = params['title'], 
				author = self.user._key
				)
		
		if not is_ok:
			# show userform with error messages
			self._serve(**params)
			return
		
		post_key = post.put() # save
		self.redirect(self.uri_for('blog-post',  post_id = post_key.id() ))
		
	def _serve(self, **params):
		self.render('blog-edit.html', new=True, **params)
		
		
class BlogEdit(RequestHandler):
	@user_required
	def get(self, post_id):
		post = Post.get_by_id(int(post_id))
		
		if not post:
			self.abort(404)
		
		if not _user_is_author(self.user, post):
			self.abort(403)
			
		self._serve(title=post.title, content=post.content)
	
	@user_required
	def post(self, post_id):
		post = Post.get_by_id(int(post_id))
		
		if not post:
			self.abort(404)
		
		if not _user_is_author(self.user, post):
			self.abort(403)
		
		is_ok, params = _verify_post_params(self.request)
		if not is_ok:
			# show userform with error messages
			self._serve(**params)
			return
		
		post.title = params['title']
		post.content = params['content']
		post.put() # save
		self.redirect(self.uri_for('blog-post',  post_id = post.key.id() ))
		
	def _serve(self, **params):
		self.render('blog-edit.html', **params)

class BlogPost(RequestHandler):
	def get(self, post_id):
		post = Post.get_by_id(post_id)
		
		self.render('blog-post.html', post=post)

class BlogDelete(RequestHandler):
	#FIXME: @author_required
	def get(self, post_id):
		
		self.write("Delete %s" %post_id)
		
class BlogVote(RequestHandler):
	@user_required
	def get(self, post_id):
		self.write("Vote %s" %post_id)
			

