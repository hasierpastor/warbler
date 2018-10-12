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


class UserLogViewTestCase(TestCase):
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
            resp = self.client.get("/logout", follow_redirects=True)
            # .GET WHEN KEY DOESN'T EXIST IN DICTIONARY
            self.assertEqual(session.get(CURR_USER_KEY), None)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Logged out!', resp.data)


class UserShowViewTestCase(TestCase):
    """Test show user views for users."""

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

# HOW TO TEST SEARCH/LIST?
# Test whether usernames show up in html
    def test_list_users(self):
        """Test list of users show up in html, filtered list"""

        u1 = User.signup(username="bob",
                         email="bob@bob.com",
                         password="testpassword",
                         image_url=None)

        u2 = User.signup(username="tesla",
                         email="tesla@tesla.com",
                         password="testpassword",
                         image_url=None)

        db.session.commit()

        resp_all = self.client.get("/users")
        resp_search = self.client.get("/users?q=tes")

        # import pdb
        # pdb.set_trace()

        self.assertIn(b'bob', resp_all.data)
        self.assertIn(b'tesla', resp_search.data)
        self.assertIn(b'testuser', resp_search.data)

    def test_users_show(self):
        """Test user profile is shown"""

        resp = self.client.get(f"/users/{self.testuser.id}")

        self.assertIn(b'testuser', resp.data)
        self.assertIn(b'0', resp.data)
        self.assertIn(b'<ul class="list-group" id="messages">', resp.data)


class UserFollowViewTestCase(TestCase):
    """Test user follow views."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Like.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser1",
                                     email="test1@test.com",
                                     password="testpassword",
                                     image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                     email="test2@test.com",
                                     password="testpassword",
                                     image_url=None)

        self.testuser3 = User.signup(username="testuser3",
                                     email="test3@test.com",
                                     password="testpassword",
                                     image_url=None)

        db.session.commit()

        # testuser id not available/created until id session is committed
        f1 = FollowersFollowee(followee_id=self.testuser1.id,
                               follower_id=self.testuser2.id)

        f2 = FollowersFollowee(followee_id=self.testuser2.id,
                               follower_id=self.testuser3.id)

        db.session.add_all([f1, f2])
        db.session.commit()

    def test_show_following(self):
        """Test list of user followers are shown"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser3.id

        resp = c.get(f"/users/{self.testuser3.id}/following")

        self.assertIn(b'testuser2', resp.data)
        self.assertIn(b'<div class="card user-card">', resp.data)

    def test_users_followers(self):
        """Test list of people user is following are shown"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

        resp = c.get(f"/users/{self.testuser1.id}/followers")

        self.assertIn(b'testuser2', resp.data)
        self.assertIn(b'<div class="card user-card">', resp.data)

    def test_add_follow(self):
        """Test adding follow returns followed user in html"""
        with self.client as c:
            with c.session_transaction() as sess:
                import pdb
                pdb.set_trace()
                sess[CURR_USER_KEY] = self.testuser1.id

        testfollowee = User.signup(username="testfollowee",
                                   email="testfollowee@test.com",
                                   password="testpassword",
                                   image_url=None)
        db.session.commit()

        resp_logged_in = c.post(
            f"/users/follow/{testfollowee.id}", follow_redirects='True')

        self.assertIn(b'testfollowee', resp_logged_in.data)
        self.assertIn(b'<div class="card user-card">', resp_logged_in.data)
        self.assertEqual(resp_logged_in.status_code, 200)
        import pdb
        pdb.set_trace()
        # c.get('/logout')
        sess[CURR_USER_KEY] = None
        import pdb
        pdb.set_trace()

        resp_not_logged_in = c.post(
            f"/users/follow/{testfollowee.id}", follow_redirects='True')

        self.assertIn(b'Access unauthorized.', resp_not_logged_in.data)
        self.assertEqual(resp_not_logged_in.status_code, 200)

    def test_add_follow_not_logged_in(self):
        """Test adding follow returns followed user in html"""

        with self.client as c:

            testfollowee = User.signup(username="testfollowee",
                                       email="testfollowee@test.com",
                                       password="testpassword",
                                       image_url=None)
            db.session.commit()

            resp_not_logged_in = c.post(
                f"/users/follow/{testfollowee.id}", follow_redirects='True')

        self.assertIn(b'Access unauthorized.', resp_not_logged_in.data)
        self.assertEqual(resp_not_logged_in.status_code, 200)

    # def test_stop_following(self):
    #     """Test stop follow does not return followed user in html"""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser3.id

    #     resp_logged_in = c.post(
    #         f"/users/stop-following/{self.testuser2.id}", follow_redirects='True')
    #     # resp_not_logged_in = client.post(
    #     #     f"/users/stop-following/{testuser2.id}")

    #     self.assertNotIn(b'testuser2', resp_logged_in.data)
    #     self.assertIn(b'<div class="card user-card">', resp_logged_in.data)
    #     # self.assertIn(b'Access unauthorized.', resp_not_logged_in.data)

    #     self.assertEquals(resp_logged_in.status_code, 200)
    #     # self.assertEquals(resp_not_logged_in.status_code, 200)


# class UserLikeViewTestCase(TestCase):
#     """Test user like views."""

#     def setUp(self):
#         """Create test client, add sample data."""

#         User.query.delete()
#         Message.query.delete()
#         FollowersFollowee.query.delete()
#         Like.query.delete()

#         self.client = app.test_client()

#         self.testuser1 = User.signup(username="testuser1",
#                                      email="test1@test.com",
#                                      password="testpassword",
#                                      image_url=None)

#         self.testuser2 = User.signup(username="testuser2",
#                                      email="test2@test.com",
#                                      password="testpassword",
#                                      image_url=None)

#         self.testuser3 = User.signup(username="testuser3",
#                                      email="test3@test.com",
#                                      password="testpassword",
#                                      image_url=None)

#         db.session.commit()

#         # testuser id not available/created until id session is committed
#         f1 = FollowersFollowee(followee_id=self.testuser1.id,
#                                follower_id=self.testuser2.id)

#         f2 = FollowersFollowee(followee_id=self.testuser2.id,
#                                follower_id=self.testuser3.id)

#         db.session.add_all([f1, f2])
#         db.session.commit()

#     def test_users_likes(self):
#         """Test list of people user is following are shown"""
