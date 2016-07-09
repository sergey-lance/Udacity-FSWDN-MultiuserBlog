# -*- coding: utf-8 -*-

import time
import logging
from webapp2_extras.appengine.auth.models import User
from webapp2_extras.security import generate_password_hash

from google.appengine.ext import ndb


class User(User):

	avatar = ndb.StringProperty(required=False, default="new.png")

	def set_password(self, raw_password):
		"""Sets the password for the current user
		param raw_password:
		The raw password which will be hashed and stored
		"""
		self.password = generate_password_hash(raw_password, length=16)

	@classmethod
	def get_by_auth_token(cls, user_id, token, subject='auth'):
		"""Returns a user object based on a user ID and token.
		param user_id:
						The user_id of the requesting user.
		param token:
						The token string to be verified.
		returns:
				A tuple ``(User, timestamp)``, with a user object and
				the token timestamp, or ``(None, None)`` if both were not found.
		"""
		token_key = cls.token_model.get_key(user_id, subject, token)
		user_key = ndb.Key(cls, user_id)
		valid_token, user = ndb.get_multi([token_key, user_key])
		if valid_token and user:
			timestamp = int(time.mktime(valid_token.created.timetuple()))
			return user, timestamp

		return None, None

	@classmethod
	def get_userdata(cls, user_keys, fields=['name', 'avatar']):
		''' Fetch user info at once to save PRCs. '''
		users = ndb.get_multi(user_keys)
		users_data = (u.to_dict(include=fields) for u in users)
		return dict(zip(user_keys, users_data))


class Record(ndb.Model):  # attributes are common for posts and comments
	content = ndb.TextProperty()
	author = ndb.KeyProperty(kind=User)
	created = ndb.DateTimeProperty(auto_now_add=True)


class Comment(Record):
	# TODO:
	# locked = ndb.BooleanProperty() # True means the author of the comment can't change it anymore...
			# (because of timeout or because it had been answered by another user.)
	pass


class Post(Record):
	title = ndb.StringProperty()
	comments = ndb.KeyProperty(kind=Comment, repeated=True)
	score = ndb.IntegerProperty( required=True, default=0)  # Likes minus Dislikes
	upvoters = ndb.IntegerProperty(repeated=True)  # a list of user UIDs (numbers)
	downvoters = ndb.IntegerProperty(repeated=True)

	@ndb.transactional
	def update_score(self):
		score = len(self.upvoters) - len(self.downvoters)
		self.score = score
		self.put()
