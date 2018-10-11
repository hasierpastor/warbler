"""Unit tests for SQL Alchemy Message Model"""

import os
from unittest import TestCase

from models import db, User, Message, FollowersFollowee, Like
from datetime import datetime

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test model for User."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Delete all instances of users from test database"""

        User.query.delete()
        Message.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""

        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        m = Message(
            id=1,
            text="Test Message",
            timestamp=None,
            user_id=1
        )

        db.session.add_all([u, m])
        db.session.commit()

        # Message instance attributes should equal the ones were set, timestamp should default to datetime.utcnow()
        self.assertEqual(m.text, 'Test Message')
        self.assertEqual(m.id, 1)


# Tested in test_user_model.py

# class MessageUserRelationshipTestCase(TestCase):
#     """Test relationship between Message and User models."""


class MessageLikesRelationshipTestCase(TestCase):
    """Test relationship between messages and likes models"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Like.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Delete all instances of users from test database"""

        User.query.delete()
        Message.query.delete()
        Like.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def test_message_like_relationship(self):

        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        m = Message(
            id=1,
            text="Test Message",
            timestamp=None,
            user_id=1
        )

        l = Like(
            user_id=u.id,
            message_id=m.id
        )

        db.session.add_all([u, m, l])
        db.session.commit()

        self.assertEqual(m.likes[0].message_id, m.id)
