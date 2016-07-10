# Udacity-FSWDN-MultiuserBlog

A basic demo [GAE](cloud.google.com/appengine/ "Google App Engine") blog application, written in Python using webapp2 framework.

## About 

This app is created for FSWDN Udacity course according to this [specifications](https://review.udacity.com/#!/rubrics/150/view).
The idea and the content were inspired by www.catipsum.com. 

####  Additional features implemented:

1. User accounts implementation is based on `webapp2_extras` `User` model (secure sessions, hashed passwords, etc.).
2. Some advanced features of Jinja2 template engine are being used: marcro, filters.
3. All html-forms and some critical URIs are protected against [CSRF](https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF) "Cross-Site Request Forgery") attacks.
4. "Likes" were implemented with AJAX (with fallback to simple html links).
5. [Trumbowyg](https://alex-d.github.io/Trumbowyg/) WYSIWYG-editor for posts.
6. In-place editing for comments.
7. Flash messages for users.
8. Fancy design (kittens love it).

## How to launch it on developer's Linux machine

#### I. Download the Google App Engine SDK
1. Download the SDK from http://code.google.com/appengine/downloads.html
2. Unzip the file: `unzip google_appengine*.zip`
3. `cd google_appengine`
4. run any demo application: `./dev_appserver.py demos/python/guestbook/`
5. in a browser open http://localhost:8080/ to check it works.
6. press **Ctrl+C** to stop application server.

#### II. Run the app
0. install some dependancies:

        sudo apt-get install python-lxml python-jinja2`

1. add `google_appengine` directory to $PATH

        cd google_appengine; export PATH=$PATH:$(pwd)

2. Clone the master branch to any other directory:

        git clone https://github.com/sergey-lance/Udacity-FSWDN-MultiuserBlog.git

3. `cd Udacity-FSWDN-MultiuserBlog`
4. run the appserver in current directory:

        dev_appserver.py .

5. in a web-browser open [http://localhost:8080/](http://localhost:8080/)

## Deploy on Google Appengine

1. Create [a new project](https://console.cloud.google.com/iam-admin/projects), open the Cloud Shell. [docs](https://cloud.google.com/shell/docs/)

2. In the Cloud Shell run the following commands (substitute `<your-project-name>` with the actual name of your project):
  ```Shell
  git clone https://github.com/sergey-lance/Udacity-FSWDN-MultiuserBlog/
  cd Udacity-FSWDN-MultiuserBlog/
  appcfg.py -A <your-project-name> -V v1 update .
  ```
3. Open the URL *http://\<your-project-name\>.appspot.com/blog/* in a browser

#### Upload demo data to AppEngine
0. Create an access key for [App Engine default service account](https://console.cloud.google.com/iam-admin/iam/) and set it's location to environment variable: ```export GOOGLE_APPLICATION_CREDENTIALS=/home/me/Downloads/<APP_ID-KEY_ID>.json```

1. Upload the users.dat and posts.dat to AppEngine:
  ```Shell
  appcfg.py upload_data --url=http://APPNAME.appspot.com/_ah/remote_api --filename=users.dat --application=s~APPNAME
  appcfg.py upload_data --url=http://APPNAME.appspot.com/_ah/remote_api --filename=posts.dat --application=s~APPNAME
  ```
  
To dump data from local server use this commands:
  ```Shell
  appcfg.py download_data --url=http://localhost:8080/_ah/remote_api --filename=users.dat --kind=User
  appcfg.py download_data --url=http://localhost:8080/_ah/remote_api --filename=posts.dat --kind=Post
  ```

## Copyright and license
You are free to use this sources as you like, but do not forget about the Udacity Honor Code.
