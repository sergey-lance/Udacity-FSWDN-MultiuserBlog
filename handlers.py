#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main import RequestHandler
from google.appengine.ext import ndb

from auth import user_required

#~ Post = namedtuple('Post', ['title','content'])
#~ post = Post(title="hehe", content='con')

from models import Post, Comment, User

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

class BlogNewpost(RequestHandler):
	@user_required
	def get(self):
		self._serve()
	
	def post(self):
		title = self.request.get('title')
		content = self.request.get('content')
		
		if content:
			content = self.clean_html(content)
		
		params = dict(title=title, content=content)
		err_params = {}
		
		if not title:
			err_params['err_title'] = 'Post should have a title.'
			
		if not content: 
			err_params['error'] = 'Post should have a content.'
		
		post = Post( content = content,
				title = title, 
				author = self.user._key
				)
		
		if err_params: 
			self._serve( dict(params,post=post, **err_params))
			#~ logging.info(dict(params,**err_params))
			return

		
		post_key = post.put()
		self.redirect(self.uri_for('blog-post',  post_id = post_key.id() ) )
		
	def _serve(self, params={}):
		self.render('blog-edit.html', **params)
		

class BlogPost(RequestHandler):
	def get(self, post_id):
		post = Post.get_by_id(post_id)
		
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
			

