#!/usr/bin/env python
# encoding: utf-8
''' 
	Populate datastore with demo data.
'''

import sys, os, random
from datetime import datetime, timedelta
import logging 

try:
    import dev_appserver
    dev_appserver.fix_sys_path()
except ImportError:
    print('Please make sure the App Engine SDK is in your PYTHONPATH.')
    exit(1)

from google.appengine.ext import ndb
from google.appengine.ext.remote_api import remote_api_stub

from models import *


def populate():
	
	# Users
	user_data = [
		dict( auth_id="own:joseph", name="Joseph", email="jos@example.com", avatar='1.png', password_raw="josjos"), 
		dict( auth_id="own:mao", name="Mao", email="mao@example.com", avatar='2.jpg', password_raw="maomao"), 
		dict( auth_id="own:potty", name="Potty", email="potty@example.com", avatar='3.jpg', password_raw="potpot"), 
		dict( auth_id="own:robby", name="Robby", email="rob@example.com", avatar='4.jpg', password_raw="robrob"), 
		dict( auth_id="own:benito", name="Benito", email="benito@example.com", avatar='5.jpg', password_raw="benben"), 
		dict( auth_id="own:hitler", name="Hitler", email="furry@example.com", avatar='6.jpg', password_raw="hitlerhitler"), 
		dict( auth_id="own:kim", name="Kim", email="kim@example.com", avatar='7.jpg', password_raw="kimkim"), 
		]
	unique_properties = ['email']
	
	users = []
	for u in user_data:
		create_ok, create_info = User.create_user(unique_properties=unique_properties, **u)
		if not create_ok:
			logging.warn('Failed to create user "%s"' % u['auth_id'])
		else:
			users.append(create_info)
	
	if not users:
		logging.error("No users created. The end.")
		exit(1)
	
	def randdate():
		now = datetime.utcnow()
		return now + timedelta(days = -random.randint(0,100))
		
		
	# Posts
	post_data = [
		dict( title = 'test', content="hehe"),
		dict( title = 'test', content="hehe"),
		dict( title = 'test', content="hehe"),
		dict( title = 'test', content="hehe"),
		dict( title = 'test', content="hehe"),
		dict( title = 'test', content="hehe"),
		]
	
	for p in post_data:
		# Random author
		author=random.choice(users).key
		
		# Random votes for post
		voters = random.sample(users, random.randint(0,len(users)) )
		if author in voters:
			voters.remove(author) #can't vote for his own post
			
		voters_keys = [getattr(user, 'key') for user in voters]
		r = random.randint(0, len(voters_keys))
		
		_ = Post(author = author,
				upvoters = voters_keys[:r],
				downvoters = voters_keys[r:],
				created = randdate(),
				**p)
		_.put()
	

def main():
	remote_api_stub.ConfigureRemoteApi(
		app_id=None,
		path='/_ah/remote_api',
		auth_func=lambda: ('email', 'password'),
		servername='localhost:8080')
	
	sys.stderr.write('Populating database with demo data...\n')
	populate()

if __name__ == '__main__':
	main()
