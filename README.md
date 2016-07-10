# Udacity-FSWDN-MultiuserBlog

A basic demo [GAE](cloud.google.com/appengine/ "Google App Engine") blog application, written in Python using webapp2 framework.

---
## About 
This app is created for FSWDN Udacity course according to this [specifications](https://review.udacity.com/#!/rubrics/150/view). Idea and demo content was inspired by www.catipsum.com. 

### Extra Features:
1. Users implemented with `webapp2_extras` `User` model (secure sessions, hashed passwords, etc.).
2. Jinja2 template engine used with advanced features: marcro, filters.
3. All forms and some critical URIs are protected against [CSRF](https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF) "Cross-Site Request Forgery") attacks.
4. "Likes" are implemented with AJAX (with fallback to simple html links).
5. [Trumbowyg](https://alex-d.github.io/Trumbowyg/) WYSIWYG-editor for posts.
6. In-place editing for comments.
7. Flash messages for users.
8. Fancy design (kittens do love it).

## Launching on a developer's Linux machine
#### 1. Download and try Google App Engine SDK
1. Download the SDK from http://code.google.com/appengine/downloads.html
2. Unzip a file: `unzip google_appengine*.zip`
3. `cd google_appengine`
4. run any demo application: `./dev_appserver.py demos/python/guestbook/`
5. in a browser open http://localhost:8080/ to check it works.
6. press **Ctrl+C** to stop application server.

#### 2. Get the app and run it
1. add `google_appengine` directory to $PATH: `cd google_appengine; export PATH=$PATH:$(pwd)`
2. Clone the master branch to any other directory: `git clone https://github.com/sergey-lance/Udacity-FSWDN-MultiuserBlog.git`
3. `cd Udacity-FSWDN-MultiuserBlog`
4. run the appserver: `dev_appserver.py .`
5. in a browser open http://localhost:8080/

## Deploy on Google Appengine



