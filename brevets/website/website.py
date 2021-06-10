"""
Flask-Login and Flask-WTF example
"""
from urllib.parse import urlparse, urljoin
from flask import Flask, request, render_template, redirect, url_for, flash, abort
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user, UserMixin,
                         confirm_login, fresh_login_required)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, validators

from passlib.hash import sha256_crypt as pwd_context

from itsdangerous import (TimedJSONWebSignatureSerializer \
                                  as Serializer, BadSignature, \
                                  SignatureExpired)


import requests
import time
import os

from pymongo import MongoClient

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.brevetsdb


class RegisterForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
                          message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])

    password = StringField('Password', [
        validators.Length(min=6, max=25,
                          message=u"Minimum of 6 characters required."),
        validators.InputRequired(u"Forget something?")])


class LoginForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
                          message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])

    password = StringField('Password', [
        validators.Length(min=6, max=25,
                          message=u"Minimum of 6 characters required."),
        validators.InputRequired(u"Forget something?")])

    remember = BooleanField('Remember me')


def is_safe_url(target):
    """
    :source: https://github.com/fengsp/flask-snippets/blob/master/security/redirect_back.py
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


class User(UserMixin):
    def __init__(self, id, name, hashed):
        self.id = id
        self.name = name
        self.hashed = hashed
        self.token = ''

    def set_token(self, token):
        self.token = token
        return self

USERS = {}

app = Flask(__name__)
app.secret_key = "SomeString"

app.config.from_object(__name__)

login_manager = LoginManager()

login_manager.session_protection = "strong"

login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."

login_manager.refresh_view = "login"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return USERS[str(user_id)]


login_manager.init_app(app)


@app.route("/")
def index():
    for user in db.users.find():
        username = user['username']
        hashed = user['hashed']
        USERS.update({username:User(u""+username, username, hashed)})

    return render_template("index.html")





@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit() and request.method == "POST" and "username" in request.form:
        username = request.form["username"]
        hashed =  pwd_context.using(salt=app.secret_key).encrypt(request.form["password"])

        if username and username not in USERS:
            user = requests.get('http://restapi:5000/register', params={'username': username, 'hashed': hashed})
            USERS.update({username:User(u""+username, username, hashed)})

            app.logger.debug(f"{username} registered")
            flash("Registered")
            next = request.args.get("next")
            if not is_safe_url(next):
                abort(400)
            return redirect(next or url_for('login'))
        else:
            flash('invalid username')

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form:
        username = request.form["username"]
        password = pwd_context.using(salt=app.secret_key).encrypt(request.form["password"])

        if username and username in USERS:
            if password == USERS[username].hashed:
                remember = request.form.get("remember", "false") == "true"
                if login_user(USERS[username], remember=remember):
                    flash("Logged in!")
                    flash("I'll remember you") if remember else None
                    next = request.args.get("next")
                    if not is_safe_url(next):
                        abort(400)
                    return redirect(next or url_for('token'))
            else:
                flash("Invalid password.")
        else:
            flash("Invalid username.")
    return render_template("login.html", form=form)

@app.route("/token", methods=["GET"])
@login_required
def token(expiration=600):
    #s = Serializer(app.secret_key, expires_in=expiration)

    token = requests.get('http://restapi:5000/token', params={'hashed':current_user.hashed})
    current_user.set_token(token.json()['token'])
    app.logger.debug("token set")

    return render_template("index.html")


@app.route("/times", methods = ["GET"])
@login_required
def times():
    s = Serializer(app.secret_key)
    try:
        data = s.loads(current_user.token)
    except SignatureExpired:
        flash( "Expired token!"   ) # valid token, but expired
        return render_template("index.html")
    except BadSignature:
        flash( "Invalid token!"   )
        return render_template("index.html")# invalid token

    app.logger.debug("token authorized")
    return render_template("times.html")

@app.route('/listAll')
@login_required
def listall():
    dtype = request.args.get('dtype')
    top = request.args.get('top')
    token = current_user.token
    #app.logger.debug(token)
    r = requests.get('http://restapi:5000/listAll/'+dtype, params={'token': token, 'top': top})
    return r.text

@app.route('/listOpenOnly')
@login_required
def listopen():
    dtype = request.args.get('dtype')
    top = request.args.get('top')
    token = current_user.token

    r = requests.get('http://restapi:5000/listOpenOnly/'+dtype, {'token': token, 'top': top})
    return r.text

@app.route('/listCloseOnly')
@login_required
def listclose():
    dtype = request.args.get('dtype')
    top = request.args.get('top')
    token = current_user.token

    r = requests.get('http://restapi:5000/listCloseOnly/'+dtype, {'token': token, 'top': top})
    return r.text

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
