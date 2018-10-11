"""User model tests."""

# run these tests like:
#
# python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, FollowersFollowee, Like
from datetime import datetime

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test model for User."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Like.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Delete all instances of users from test database"""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(u.messages.count(), 0)
        self.assertEqual(u.followers.count(), 0)
        self.assertEqual(u.email, 'test@test.com')
        self.assertEqual(u.__repr__(), '<User #1: testuser, test@test.com>')

    def test_signup(self):
        """Does signup process work?  Hashed password?"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="testpassword",
            image_url=None
        )

        db.session.add(u)
        db.session.commit()

        # Username should be expected; password should be a hash
        self.assertEqual(u.username, 'testuser')
        self.assertIn('$2b$12$', u.password)

    def test_authenticate(self):
        """Does authentication process work?  Does passed in password match database password?"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="testpassword",
            image_url=None
        )

        # db.session.add(u)
        db.session.commit()

        authenticated_user = User.authenticate(u.username, 'testpassword')
        unauthenticated_user = User.authenticate(u.username, 'random')

        # Correct password should return user
        # Incorrect password should return False
        self.assertEqual(authenticated_user.username, 'testuser')
        self.assertEqual(unauthenticated_user, False)


class UserMessageRelationshipTestCase(TestCase):
    # Set up and tear down have to be added for every class you create
    """Test relationship between User and Message models."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Like.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Delete all instances of users from test database"""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def test_message_relationship(self):
        """Does message relationship to user work?"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="testpassword",
            image_url=None
        )

        u.id = 1

        m = Message(
            id=1,
            text='Test message',
            user_id=u.id
        )

        # ADD 2 ITEMS AT ONCE
        db.session.add(m)
        db.session.commit()

        # Is message text the same as user-linked message text?
        # Is user_id of message same as user's id?
        self.assertEqual(u.messages[0].text, 'Test message')
        self.assertEqual(u.id, m.user_id)

        # Testing relationship between messages and users - SHOULD IT BE IN MESSAGE TESTS??

        self.assertEqual(m.user.username, 'testuser')


class UserFollowersFolloweeRelationshipTestCase(TestCase):
    """Test relationship between User and FollowersFollowee models."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Like.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Delete all instances of users from test database"""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def test_follow_relationship(self):
        """Does follow relationship to user work?
        Create 3 users for chain of u1 followed by u2, u2 followed by u3"""

        # HOW TO FIX AUTOINCREMENT ID's?
        u1 = User.signup(
            email="test1@test.com",
            username="testuser1",
            password="testpassword",
            image_url=None
        )

        u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="testpassword",
            image_url=None
        )

        u3 = User.signup(
            email="test3@test.com",
            username="testuser3",
            password="testpassword",
            image_url=None
        )

        db.session.commit()

        f1 = FollowersFollowee(
            followee_id=u1.id,
            follower_id=u2.id
        )

        f2 = FollowersFollowee(
            followee_id=u2.id,
            follower_id=u3.id
        )

        db.session.add_all([f1, f2])
        db.session.commit()

        # USERS GO THROUGH FOLLOWS TABLE AND BACK TO USER TABLE
        # FOLLOWING = u1 is FOLLOWED by u2
        # FOLLOWERS = u3 is FOLLOWING u2
        self.assertEqual(u1.followers[0].id, u2.id)
        self.assertEqual(u3.following[0].id, u2.id)

        # # Test is_followed_by, is_following methods
        self.assertEqual(u1.is_followed_by(u2), True)
        self.assertEqual(u2.is_followed_by(u1), False)
        self.assertEqual(u3.is_following(u2), True)
        self.assertEqual(u2.is_following(u3), False)


class UserLikeRelationshipTestCase(TestCase):
    """Test relationship between User and Like models."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Like.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Delete all instances of users from test database"""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def test_user_like_relationship(self):

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="testpassword",
            image_url=None
        )

        u.id = 1

        m = Message(
            id=1,
            text="Test Message",
            timestamp=None,
            user_id=u.id
        )

        l = Like(
            user_id=u.id,
            message_id=m.id
        )

        db.session.add_all([m, l])
        db.session.commit()

        self.assertEqual(u.likes[0].user_id, u.id)
