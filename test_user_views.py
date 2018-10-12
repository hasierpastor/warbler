"""Unit tests for User View App Routes"""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from flask import session
from models import db, connect_db, Message, User, FollowersFollowee, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY, do_login

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserSignupViewTestCase(TestCase):
    """Test signup views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Like.query.delete()

        self.client = app.test_client()

        # self.testuser = User.signup(username="testuser",
        #                             email="test@test.com",
        #                             password="testuser",
        #                             image_url=None)

        # db.session.commit()

    def test_signup_form_rendered(self):
        """Can use sign up a user? - once form is validated"""

        resp = self.client.get('/signup')

        self.assertEqual(resp.status_code, 200)
        self.assertIn(
            b'<h2 class="join-message">Join Warbler today.</h2>', resp.data)

        # with self.client as c:
        #     with c.session_transaction() as sess:
        #         sess[CURR_USER_KEY] = self.testuser.id

        # # Now, that session setting is saved, so we can have
        # # the rest of ours test

        #     resp = c.post("/messages/new", data={"text": "Hello"})

    def test_signup_submitted_not_validated(self):
        """If user signup form is not validated the form should be rendered again"""

        # set password too short
        resp = self.client.post("/signup", data={"username": "testuser",
                                                 "email": "test@test.com",
                                                 "password": "a",
                                                 "image_url": None})

        self.assertEqual(resp.status_code, 200)
        self.assertIn(
            b'Field must be at least 6 characters long', resp.data)

    def test_signup_validated(self):
        """If user signup form is validated, user is added to database and redirect to homepage"""

        resp = self.client.post("/signup", data={"username": "testuser",
                                                 "email": "test@test.com",
                                                 "password": "testpassword",
                                                 "image_url": None}, follow_redirects=True)

        signed_up_user = User.query.all()

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'<ul class="user-stats nav nav-pills">', resp.data)
        self.assertEqual(signed_up_user[0].username, 'testuser')


class UserLoginViewTestCase(TestCase):
    """Test login views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Like.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testpassword",
                                    image_url=None)

        db.session.commit()

    def test_login_form_rendered(self):
        """Test login form shown"""

        resp = self.client.get('/login')

        self.assertEqual(resp.status_code, 200)
        self.assertIn(
            b'<h2 class="join-message">Welcome back.</h2>', resp.data)

    def test_login_submitted_not_validated(self):
        """If user login form is not validated the form should be rendered again"""

        # set wrong username and password
        resp = self.client.post("/login", data={"username": "wronguser",
                                                "password": "wrongpassword"})

        self.assertEqual(resp.status_code, 200)
        self.assertIn(
            b'Invalid credentials', resp.data)

    def test_login_validated(self):
        """If user login form is validated, log in user and redirect to homepage"""

        with self.client:
            resp = self.client.post("/login", data={"username": "testuser",
                                                    "password": "testpassword"}, follow_redirects=True)
            self.assertEqual(session[CURR_USER_KEY], self.testuser.id)

        signed_up_user = User.query.all()

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'<ul class="user-stats nav nav-pills">', resp.data)
        self.assertEqual(signed_up_user[0].username, 'testuser')

    def test_logout(self):
        """Test that user can log out correctly"""

        with self.client:
            self.client.post("/login", data={"username": "testuser",
                                             "password": "testpassword"}, follow_redirects=True)

            # import pdb
            # pdb.set_trace()
            resp = self.client.get("/logout", follow_redirects=True)
            # .GET WHEN KEY DOESN'T EXIST IN DICTIONARY
            self.assertEqual(session.get(CURR_USER_KEY), None)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Logged out!', resp.data)
