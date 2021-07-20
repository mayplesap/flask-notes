"""Flask app for Flask note app."""

from flask import Flask, render_template, request, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Note

from forms import AddNoteForm, LoginForm, RegisterForm

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

    return redirect("/register")

@app.route("/register", methods=['GET', 'POST'])
def register():
    """Displays a form to register a new user"""
    
    form = RegisterForm()

    if form.validate_on_submit():

        user = User.register(username=form.username.data, 
                             pwd=form.password.data, 
                             email=form.email.data, 
                             first_name=form.first_name.data, 
                             last_name=form.last_name.data)

        db.session.add(user)
        db.session.commit()

        session['username'] = user.username
        return redirect(f'/users/{user.username}')


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
            return redirect(f'/users/{username}')
        else:
            form.username.errors = ['Bad username/password']


    return render_template('login.html', form=form)

# @app.route("/secret")
# def secret():
#     """If authenticated, displays secret.html otherwise redirects to /login"""

#     if "username" not in session:
#         flash("You must be logged in!")
#         return redirect("/login")

#     return render_template("secret.html")

@app.route("/logout", methods=['POST'])
def logout():
    """Logs user out and redirects to /login"""

    session.pop("username", None)

    return redirect("/login") #login for now unless homepage

@app.route("/users/<username>")
def user_detail(username):
    """TODO"""

    user = User.query.get(username)
    notes = user.notes

    if 'username' not in session:
        flash("You must be logged in!")
        return redirect("/login")
    elif session['username'] != username:
        flash("Not your account!!")
        return redirect(f"/users/{session['username']}")

    return render_template("user_detail.html", user=user, notes=notes)

@app.route('/users/<username>/delete')
def delete_user(username):
    """TODO"""
    user = User.query.get(username)
    notes = user.notes

    if 'username' not in session:
        flash("You must be logged in!")
        return redirect("/login")
    elif session['username'] != username:
        flash("Not your account!!")
        return redirect(f"/users/{session['username']}")

    db.session.delete(notes)
    db.session.delete(user)
    session.pop("username", None)

    db.session.commit()
    return redirect('/')

############################### NOTES ###############################

@app.route('/users/<username>/notes/add', methods=['GET', 'POST'])
def add_note(username):
    """TODO"""

    form = AddNoteForm()

    if 'username' not in session:
        flash("You must be logged in!")
        return redirect("/login")
    elif session['username'] != username:
        flash("Not your account!!")
        return redirect(f"/users/{session['username']}")

    if form.validate_on_submit():
        note = Note(title=form.title.data, content=form.content.data, owner=username)

        db.session.add(note)
        db.session.commit()

        return redirect(f'user/{username}')

    return render_template('add_note.html', form=form)

