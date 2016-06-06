#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main import RequestHandler


class LoginHandler(RequestHandler):
	def get(self):
		self.write("Login")

class LogoutHandler(RequestHandler):
	def get(self):
		self.write("Logout")
		
class SignupHandler(RequestHandler):
	def get(self):
		self.write("Signup")
