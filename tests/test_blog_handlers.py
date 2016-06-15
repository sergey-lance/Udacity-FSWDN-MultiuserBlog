# encoding: utf-8
import unittest
import os
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from main import app

class BlogTests(unittest.TestCase):
	def setUp(self):
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		ndb.get_context().clear_cache()
		
	def test_blog_frontpage(self):
		rv = app.get_response('/blog/')
		assert rv.status == '200 OK'
		assert "</html>" in rv.body
