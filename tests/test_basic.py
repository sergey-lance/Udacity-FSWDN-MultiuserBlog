# encoding: utf-8
import unittest
from main import app

class BasicTest(unittest.TestCase):
	def test_home_redirects(self):
		rv = app.get_response('/')
		assert rv.status == '302 FOUND' or \
				rv.status == '301 Moved Permanently'
