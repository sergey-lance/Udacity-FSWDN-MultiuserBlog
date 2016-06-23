#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import logging

from google.appengine.ext import ndb
from lxml.html.clean import Cleaner

from main import RequestHandler, csrf_check
from auth import user_required
from models import Post, Comment, User


ALLOW_TAGS = [ 'a', 'em', 'strong', 'del', 'ins', 'br', 'p', #symantic tags
		'li', 'ol', 'ul', #lists
		'abbr', 'acronym','sub', 'sup', 'pre', 'code', #some harmless tags
		]
		
_html_cleaner = Cleaner(
		safe_attrs_only = True,
		add_nofollow=True,
		allow_tags = ALLOW_TAGS,
		remove_unknown_tags = False, #need this
		)
		
def _clean_html(content_html):
	if not content_html:
		return ""
	return _html_cleaner.clean_html(content_html)
	
	

def _user_is_author(user, obj_instance):
	if user.key == obj_instance.author:
		return True
	else:
		return False


class WelcomeHandler(RequestHandler):
	@user_required
	def get(self):
		self.render('welcome.html')
	
# Blog
class BlogRequestHandler(RequestHandler):
	def _grab_post(self, post_id):
		post = Post.get_by_id(int(post_id))
		if not post:
			self.abort(404, explanation = "No such Post.")
		return post


class BlogFrontpage(BlogRequestHandler):
	def get(self):
		# Posts
		posts = Post.query().order(-Post.created).fetch(20) #TODO: pagination
		
		# Users
		user_keys = set((p.author for p in posts)) 
		users = ndb.get_multi(user_keys) #fetch user records at once to save PRCs.
		users_data = (u.to_dict(include=['name', 'avatar']) for u in users)
		users_dict = dict(zip(user_keys, users_data))
		
		self.render('blog-frontpage.html', posts=posts, users_dict=users_dict)


class BlogOnePost(BlogRequestHandler):
	def get(self, post_id):
		post = self._grab_post(post_id)
		
		author_dict = post.author.get().to_dict(include=['name', 'avatar'])
		comments = ndb.get_multi(post.comments)
		
		# purge absent comments from list
		absent_comment_idxs = [idx for idx, x in enumerate(comments) if x is None]
		if absent_comment_idxs:
			for i in absent_comment_idxs:
				del post.comments[i]
			post.put() #save post
			
		comments = filter(None, comments)
		comment_authors_keys = [c.author for c in comments if hasattr(c, 'author') ]
		users_dict = User.get_userdata(comment_authors_keys, fields = ['name', 'avatar'])
		
		#edit mode for certan comment
		editor_for_comment = self.request.get('edit_comment')[0:] 
		
		params = dict(
			post = post,
			post_id = post_id,
			comments = comments, 
			author_dict = author_dict,
			users_dict = users_dict,
			editor_for_comment = editor_for_comment, 
		)
		
		self.render('blog-onepost.html', **params)


def _verify_post_params(request):
	''' 
	Get and clean up parameters from request.
	Returns a tuple: (is_ok, template parameters)
	'''
	is_ok = True
	title = ''
	content = '' 
	try:
		title = request.POST['title'] # using POST instead of .get()
		content = request.POST['content-html']
	
	except KeyError: #both fields should present in POST
		is_ok = False
		
	#TODO: strip tags title = 
	content = _clean_html(content)
	
	params = dict(title=title, content=content)
	
	if not title:
		is_ok = False
		params['err_title'] = 'Post should have a title.'
		
	if not content:
		is_ok = False
		params['error'] = 'Post should have a content.'
	
	return is_ok, params


class BlogNewpost(BlogRequestHandler):
	@user_required
	def get(self):
		self._serve()
	
	@user_required
	@csrf_check
	def post(self):
		is_ok, params = _verify_post_params(self.request)
		if not is_ok:
			# show userform with error messages
			self._serve(**params)
			return
			
		post = Post( content = params['content'],
				title = params['title'], 
				author = self.user._key
				)
		
		post_key = post.put() # save
		self.redirect(self.uri_for('blog-onepost',  post_id = post_key.id() ))
		
	def _serve(self, **params):
		self.render('blog-edit.html', new=True, **params)


class BlogEdit(BlogRequestHandler):
	@user_required
	def get(self, post_id):
		post = self._grab_post(post_id)
		if not _user_is_author(self.user, post):
			self.abort(403)
		
		self._serve(post_id = post_id, title=post.title, content=post.content)
	
	@user_required
	@csrf_check
	def post(self, post_id):
		post = self._grab_post(post_id)
		
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
		self.redirect(self.uri_for('blog-onepost',  post_id = post.key.id() ))
		
	def _serve(self, **params):
		self.render('blog-edit.html', **params)


class BlogDelete(BlogRequestHandler):
	def get(self, post_id):
		# calling with get is probably a user's mistake. redirect silently.
		self.redirect(self.uri_for('blog-edit', post_id=post_id))
	
	@csrf_check
	def post(self, post_id): 
		post = self._grab_post(post_id)
		
		if not _user_is_author(self.user, post):
			self.abort(403)
		
		post.key.delete()
		time.sleep(0.1) #fix: a ghost of deleted entry appears on homepage after redirect.
				# So wait a little bit and let ndb to invalidate caches.
				# There must be a better solution.
		
		self.redirect(self.uri_for('home'))

# Comments
class CommentRequestHandler(RequestHandler):
	def _grab_post(self, post_id):
		post = Post.get_by_id(int(post_id))
		if not post:
			self.abort(404, explanation = "No such Post.")
		return post
		
	def _grab_comment(self, comment_id):
		comment = Comment.get_by_id(int(comment_id))
		if not comment:
			self.abort(404, explanation = "No such Comment.")
		return comment


class PostComment(CommentRequestHandler):
	@user_required
	def post(self, post_id):
		post = self._grab_post(post_id)
		
		try:
			comment_html = self.request.POST['comment-html']
		except KeyError: # absent data 
			self._serve(post_id)
			return

		if not comment_html: #empty comment 
			self._serve(post_id)
			return
			
		comment_html = _clean_html(comment_html)
		
		comment = Comment( 
				content = comment_html,
				author = self.user._key
				)
		
		comment_key = comment.put() # save comment
		post.comments.append(comment_key)
		post.put() #save post
		self._serve(post_id)
		
	def _serve(self, post_id):
		self.redirect(self.uri_for('blog-onepost',post_id = post_id))

		
class EditComment(CommentRequestHandler):
	@user_required
	def get(self, post_id, comment_id):
		''' Show edit form '''
		post = self._grab_post(post_id)
		comment = self._grab_comment(comment_id)
		
		if not _user_is_author(self.user, comment):
			self.abort(403)
			
		self.redirect(self.uri_for('blog-onepost', post_id = post_id,
				edit_comment=comment_id, #show editor for this comment
			))
		
	@csrf_check	
	def post(self, post_id, comment_id):
		post = self._grab_post(post_id)
		comment = self._grab_comment(comment_id)
		
		try:
			comment_html = self.request.POST['comment-html']
		except KeyError: # absent data 
			self._serve(post_id)
			return

		comment_html = _clean_html(comment_html)
		if not comment_html: #empty comment 
			self._serve(post_id)
			return
			
		comment.content = comment_html
		comment.put()
		
		#TODO: Flash "Saved"
		
		self._serve(post_id)
		
	def _serve(self, post_id):
		self.redirect(self.uri_for('blog-onepost',  post_id = post_id))
	

class DeleteComment(CommentRequestHandler):
	@user_required
	@csrf_check
	def post(self, post_id, comment_id):
		post = self._grab_post(post_id)
		comment = self._grab_comment(comment_id)
		
		try:
			post.comments.remove(comment.key)
		except ValueError: #not in list
			self.abort(404, explanation="Comment doesn't belong to that Post.")
		
		comment.key.delete()
		post.put()
		
		#TODO: flash a message
	
		self.redirect(self.uri_for('blog-onepost',post_id = post_id))

# Ratings

class BlogVote(RequestHandler):
	@user_required
	def get(self, post_id):
		self.write("Vote %s" %post_id)
			

