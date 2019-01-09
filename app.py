import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized
from sqlalchemy import and_

from forms import UserAddForm, LoginForm, MessageForm, UserEditForm
from models import db, connect_db, User, Message, Like

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        # g.likes = Like.query.filter(Like.user_id == g.user.id).all()
        # g.likes_id = [like.message_id for like in g.likes]

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        # del session[CURR_USER_KEY]
        session.pop(CURR_USER_KEY)
        flash('Logged out! :(')
        return redirect('/login')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.data['username'],
                password=form.data['password'],
                email=form.data['email'],
                image_url=form.data['image_url'] or None,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.data['username'],
                                 form.data['password'])

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


# WHY SEPARATE TO TWO FUNCTIONS?
@app.route('/logout')
def logout():
    """Handle logout of user."""
    # IMPLEMENT THIS

    return do_logout()

##############################################################################
# General user routes:


@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)
    count = Like.query.filter(Like.user_id == user.id).count()
    return render_template('users/show.html', user=user, count=count)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template('users/followers.html', user=user)


@app.route('/users/<int:user_id>/likes')
def users_likes(user_id):
    """Show list of likes of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # Removed likes/likes_id from g; refactored to pull just message_id from likes table
    likes_id = db.session.query(Like.message_id).filter(
        Like.user_id == user_id).all()
    user = User.query.get_or_404(user_id)
    messages = Message.query.filter(Message.id.in_(likes_id)).all()
    return render_template('users/likes.html', user=user, messages=messages)

#####################
# CUSTOM DECORATORS #
#####################


# def time_fn(fn):
#     def inner(*args, **kwargs):
#         start = time-now
#         fn(*args, **kwargs)
#         end = time-now
#         print("this took", end-start)
#     return inner

# # closure and "decorator function"


# def require_login(fn):
#     def inner(*args, **kwargs):
#         if g.user is None:
#             flash, redirect + return
#         else:
#             fn(*args, **kwargs)
#     return inner


# @app.route('/users/follow/<int:follow_id>', methods=['POST'])
# # @require_login
# def add_follow(follow_id):
#     """Add a follow for the currently-logged-in user."""

#     validate_logged_in_or_redirect_now()
#     # if redirection:
#     #     return redirect

#     # if not g.user:
#     #     flash("Access unauthorized.", "danger")
#     #     return redirect("/")

#     followee = User.query.get_or_404(follow_id)
#     g.user.following.append(followee)
#     db.session.commit()

#     return redirect(f"/users/{g.user.id}/following")

# WILL FUNCTION CALLED WITHIN REQUEST HAVE G.USER DEFINED?


# def validate_logged_in():
#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         raise XXXXX
#         # return redirect("/")


#################
# END DECORATOR #
#################


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followee = User.query.get_or_404(follow_id)
    g.user.following.append(followee)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followee = User.query.get(follow_id)
    g.user.following.remove(followee)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    # IMPLEMENT THIS
    if CURR_USER_KEY in session:
        user = User.query.get_or_404(session[CURR_USER_KEY])
        username_original = user.username
        form = UserEditForm(obj=user)

        if form.validate_on_submit():

            password = form.data['password']

            if User.authenticate(username_original, password):
                user.username = form.data['username']
                user.email = form.data['email']
                user.image_url = form.data['image_url'] or "/static/images/default-pic.png"
                user.header_image_url = form.data['header_image_url']
                user.bio = form.data['bio']
                db.session.commit()
                return redirect(f'/users/{user.id}')
            else:
                flash('Username or password invalid! :(')
                return redirect('/')
        else:
            return render_template('users/edit.html', form=form, user=user)
    else:
        raise Unauthorized()


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.data['text'])
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followees
    """

    if g.user:
        following_ids = [f.id for f in g.user.following] + [g.user.id]

        # FILTER(TABLENAME.COLUMNNAME.IN_(ARRAY))
        messages = (Message
                    .query
                    .filter(Message.user_id.in_(following_ids))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        # Refactor to pull message_id as tuples in likes table and pass into Jinja
        # Use list comprehension to unpack tuples before passing to Jinja - more efficient
        # COULD use secondary relationship between users and messages through likes -- about the same?
        likes_tuple = db.session.query(Like.message_id).filter(
            Like.user_id == g.user.id).all()
        likes_id = [like[0] for like in likes_tuple]
        return render_template('home.html', messages=messages, likes_id=likes_id)

    else:
        return render_template('home-anon.html')

# Refactored like and unlike routes to one app route


@app.route('/like/<action>', methods=["POST"])
def handle_like(action):
    """Handle liked message"""
    message_id = request.form.get('message_id')
    user_id = g.user.id
    if action == 'add':
        like = Like(message_id=message_id, user_id=user_id)
        db.session.add(like)
    else:
        like = Like.query.filter(
            and_(Like.user_id == user_id, Like.message_id == message_id)).first()
        db.session.delete(like)
    db.session.commit()
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
