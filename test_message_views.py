"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message_form_is_validated(self):
        """Can use add a message? - once form is validated"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        # Now, that session setting is saved, so we can have
        # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

        # Make sure it redirects
        self.assertEqual(resp.status_code, 302)

        msg = Message.query.one()
        self.assertEqual(msg.text, "Hello")

    def test_add_message_form_not_validated(self):
        """If add message form is not validated the form should be rendered again"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get("/messages/new")

        self.assertEqual(resp.status_code, 200)
        self.assertIn(
            b'<button class="btn btn-outline-success btn-block">Add my message!</button>', resp.data)

    def test_show_messages(self):
        """Testing that messages show correctly"""

        m = Message(
            id=1,
            text="Test Message",
            timestamp=None,
            user_id=self.testuser.id
        )

        db.session.add(m)
        db.session.commit()

        resp = self.client.get(f'/messages/{m.id}')

        self.assertEqual(resp.status_code, 200)
        self.assertIn(
            b'  <div class="message-heading">', resp.data)
        self.assertEqual(m.text, 'Test Message')

    def test_delete_messages(self):
        """Test that messages are deleted correctly"""

        # with self.client needs to be first... WHY???
        # with self.client as c:
        #     with c.session_transaction() as sess:
        #         sess[CURR_USER_KEY] = self.testuser.id

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message(
                id=1,
                text="Test Message",
                timestamp=None,
                user_id=self.testuser.id
            )

            db.session.add(m)
            db.session.commit()

            resp = c.post(f'/messages/{m.id}/delete')

        # Make sure it redirects
        self.assertEqual(resp.status_code, 302)

        # Query messages, if message is deleted correclty count should equal 0
        msg_count = Message.query.count()

        self.assertEqual(msg_count, 0)

    def test_delete_messages(self):
        """Test that messages are deleted correctly"""

        m = Message(
            id=1,
            text="Test Message",
            timestamp=None,
            user_id=self.testuser.id
        )

        db.session.add(m)
        db.session.commit()

        # Doesn't work when with condition comes after message add/commit
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f'/messages/{m.id}/delete')

        # Make sure it redirects
        self.assertEqual(resp.status_code, 302)

        # Query messages, if message is deleted correclty count should equal 0
        msg_count = Message.query.count()

        self.assertEqual(msg_count, 0)
