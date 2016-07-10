# -*- coding: utf-8 -*-

# Inspired by : https://github.com/abahgat/webapp2-user-accounts

from google.appengine.ext import ndb
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

from main import RequestHandler, csrf_check

# Docs:
# https://webapp-improved.appspot.com/_modules/webapp2_extras/appengine/auth/models.html
# https://webapp-improved.appspot.com/_modules/webapp2_extras/auth.html

# csrf http://stackoverflow.com/questions/8384729/is-there-any-available-solution-to-provide-xsrf-csrf-support-for-google-app-engi
# https://gist.github.com/jgeewax/2942374


def user_required(handler):
    """ Decorator that checks if there's a user associated with the current session.
        Will also fail if there's no session present.
    """

    def check_login(self, *args, **kwargs):
        auth = self.auth
        if not auth.get_user_by_session():
            self.redirect(self.uri_for('login'), abort=True)
        else:
            return handler(self, *args, **kwargs)

    return check_login


class LoginHandler(RequestHandler):

    def get(self):
        self._serve()

    def post(self):
        try:
            username = self.request.POST['username']
            password = self.request.POST['password']

        except KeyError:  # something misterious is happening
            self._serve()
            return

        params = dict(username=username)

        if not username or not password:
            params['err_password'] = 'Enter username and password, please.'
            self._serve(params)
            return

        auth_id = "own:" + username.lower()
        try:
            u = self.auth.get_user_by_password(
				auth_id, password,
				remember=True,
				save_session=True,
				)
            self.redirect(self.uri_for('welcome'))

        except InvalidAuthIdError as e:
            params['err_username'] = 'No such user.'

        except InvalidPasswordError as e:
            params['err_password'] = 'Wrong password.'

        self._serve(params)

    def _serve(self, params={}):
        self.render('login.html', **params)


class LogoutHandler(RequestHandler):

    @csrf_check     # to prevent the things like "<img src='/logout'>"
    def get(self):
        self.auth.unset_session()
        self.redirect(self.uri_for('home'))


import re
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def valid_username(username):
    return username and USER_RE.match(username)


def valid_email(email):
    return (email == "") or EMAIL_RE.match(email)


class SignupHandler(RequestHandler):

    def get(self):
        if self.user:  # already logged in
            self.abort(406, 'Already logged in.')
        self._serve()

    def post(self):
        if self.user:  # already logged in
            # redirect silently since user probably a user's mistake
            self.redirect(self.uri_for('home'))

        try:
            username = self.request.POST['username']
            password = self.request.POST['password']
            verify = self.request.POST['verify']
            email = self.request.POST['email']

        except KeyError:
            # this can't normally happen
            self._serve()

        params = dict(username=username, email=email)
        err_params = {}

        # Verify entries

        if not valid_email(email):
            err_params['err_email'] = 'Email seems to be not valid.'

        if not valid_username(username):
            err_params['err_username'] = 'Username can contain only letters, '\
                'numbers, dashes (-) and underscores (_).'

        if password == "":
            err_params['err_password'] = 'You have to set a password.'

        if password != verify:
            err_params['err_verify'] = 'Passwords doesn\'t match.'

        if err_params:
            self._serve(dict(params, **err_params))
            return

        # Create user
        unique_properties = []
        if email:
            unique_properties.append('email')

        auth_id = 'own:' + username.lower()

        create_ok, create_info = self.user_model.create_user(
                auth_id,
                unique_properties,
                email=email,
                password_raw=password,
                name=username,
                )

        # TODO: avatar upload to BlobStor.

        if not create_ok:
            # if failed, create_info is a list of non-unique properties
            if 'auth_id' in create_info:
                params['err_username'] = 'This username is already taken.'

            if 'email' in create_info:
                params['err_email'] = "This email is already registered. <br>" \
                    "If you forgot the password, there is no hope since password restore is not implemented. =("  # TODO

            self._serve(params)
            return

        user = create_info  # if ok, create_info is a User instance
        user_dict = self.auth.store.user_to_dict(user)

        self.auth.set_session(user_dict)  # Authenticate user
        self.redirect(self.uri_for('welcome'))

    def _serve(self, params={}):
        self.render('signup.html', **params)
