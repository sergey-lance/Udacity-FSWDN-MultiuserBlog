#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main import RequestHandler

class PostComment(RequestHandler):
	def get(self, post_id):
		self.write("COmment")

class EditComment(RequestHandler):
	def get(self, comment_id):
		self.write("COmment -edit")

class DeleteComment(RequestHandler):
	def get(self, comment_id):
		self.write("COmment -delete")

