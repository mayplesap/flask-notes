"""Flask app for Flask note app."""

from flask import Flask, render_template, request, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

from forms import LoginForm, RegisterForm

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret"

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///flask_notes"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route("/")
def root():
    """Redirects to register page."""

    redirect ("/register")

@app.route("/register", methods=['GET', 'POST'])
def register():
    """Displays a form to register a new user"""
    
    form = RegisterForm()

    if form.validate_on_submit():

        user = User(username=form.username.data, password=form.password.data, email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)

        db.session.add(user)
        db.session.commit()

        session['username'] = user.username
        return redirect('/secret')


    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """Displays a form to login a new user"""
    
    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect('/secret')
        else:
            form.username.errors = ['Bad username/password']


    return render_template('login.html', form=form)

