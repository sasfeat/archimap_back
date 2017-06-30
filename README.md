# Web map of architecture(backend)

### How to set up the app

#### 1. Localhost

...

#### 2. Heroku
Assume that you already have heroku account
1. Login to heroku using your email and pwd
```
$ heroku login
```
2. Create the application. Attention! The name of the app will be included at the link of your website
```
$ heroku create archimap
```
3. Create postgresql account. Hobby-dev is the only free account with 10000 rows limitation. Got to heroku website to get the info about the other limitations
```
$ heroku addons:add heroku-postgresql:hobby-dev
```
Then maybe need to wait for a while. To check the status use:
```
$ heroku pg:wait
```
4. Get your POSTGRESQL URI:
```
$ heroku config -s | grep DATABASE_URL
```
5. Install webserver e.g. gunicorn

```
$ pip install gunicorn
```
6. Create file runp-heroku.py
7. Create file Procfile
8. Generate requirements.txt:
```
$ pip freeze > requirements.txt
```
9. Push the code to heroku:
```
$ git push heroku master
```