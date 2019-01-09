# Warbler

![Warbler Snapshot](/warbler01.png?raw=true 'Warbler Snapshot')

Warbler is a Python concept app to mimic the capabilities of Twitter. Users can create accounts to log in and search for other users. Users can follow and unfollow other users, as well as like and unlike posts from those followed users.

The website is built with a Flask backend. Data is stored with Postgres and managed through SQLAlchemy. The frontend is Jinja-templated.

## Getting Started

From cloned repo folder create and activate Python virtual environment:

```
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

Create Postgres database **warbler** and seed with data:

```
createdb warbler
python seed.py
```

Start up server:

```
flask run
```

App should start running with Jinja-templated frontend.

## App Features

Account creation is required to explore features of the app. Valid email address is _not_ required, but password is hashed and account is authenticated using [bcrypt](https://www.npmjs.com/package/bcrypt).

Once logged in, user can post new messages on their feed. They can also explore and search through randomly generated list users. Selecting a user will display that user's profile and posted messages.

Users can follow/unfollow other users, and like/unlike posts from them by clicking stars. Followed users, following users, and liked posts are all listed under the current user's profile page.

Users can update or delete their profile, but need to enter their valid password to authenticate.

## Built With

- [Flask](http://flask.pocoo.org/) - Backend framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM for data management
- [Postgres](https://www.postgresql.org/) - Relational Database System
- [Jinja](http://jinja.pocoo.org/) - Frontend template

## Future Features

- Dynamic live-search without clicking submit button
- Direct message to specific users
- Enable retweeting feature
