"""Flask app for Flask note app."""

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Note

from forms import NoteForm, LoginForm, RegisterForm, DeleteForm

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret"

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///flask_notes"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

toolbar = DebugToolbarExtension(app)

SESSION_USERNAME = 'username'

connect_db(app)
db.create_all()

@app.route("/")
def root():
    """Redirects to register page."""

    return redirect("/register")

@app.route("/register", methods=['GET', 'POST'])
def register():
    """Displays a form to register a new user"""

    if 'username' in session:
        return redirect(f"/users/{session[SESSION_USERNAME]}")

    form = RegisterForm()

    if form.validate_on_submit():

        user = User.register(username=form.username.data, 
                             pwd=form.password.data, 
                             email=form.email.data, 
                             first_name=form.first_name.data, 
                             last_name=form.last_name.data)

        db.session.add(user)
        db.session.commit()

        session[SESSION_USERNAME] = user.username
        return redirect(f'/users/{user.username}')


    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """Displays a form to login a new user"""
    
    if 'username' in session:
        return redirect(f"/users/{session[SESSION_USERNAME]}")

    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session[SESSION_USERNAME] = user.username
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

    return redirect("/login")

############################### USER ###############################

@app.route("/users/<username>")
def user_detail(username):
    """Displays user detail if authenticated & authorized"""

    user = User.query.get_or_404(username)

    if 'username' not in session:
        flash("You must be logged in!")
        return redirect("/login")
    elif session[SESSION_USERNAME] != username:
        flash("Not your account!!")
        return redirect(f"/users/{session[SESSION_USERNAME]}")
    
    form = DeleteForm()
    notes = user.notes

    if form.validate_on_submit():
        return redirect(f"/users/{username}/delete")

    return render_template("user_detail.html", user=user, notes=notes, form=form)

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Deletes user and user's notes if authenticated & authorized"""

    user = User.query.get_or_404(username)

    if 'username' not in session:
        flash("You must be logged in!")
        return redirect("/login")
    elif session[SESSION_USERNAME] != username:
        flash("Not your account!!")
        return redirect(f"/users/{session[SESSION_USERNAME]}")
    
    Note.query.filter(Note.owner == username).delete()
    db.session.delete(user)
    db.session.commit()
    session.pop("username", None)
    # session.clear()

    flash("User successfully deleted")
    return redirect('/register')

############################### NOTES ###############################

@app.route('/users/<username>/notes/add', methods=['GET', 'POST'])
def add_note(username):
    """Display add_note.html and lets user add a note if authenticated & authorized"""

    if 'username' not in session:
        flash("You must be logged in!")
        return redirect("/login")
    elif session[SESSION_USERNAME] != username:
        flash("Not your account!!")
        return redirect(f"/users/{session[SESSION_USERNAME]}")
    
    form = NoteForm()

    if form.validate_on_submit():
        note = Note(title=form.title.data, content=form.content.data, owner=username)

        db.session.add(note)
        db.session.commit()

        return redirect(f'/users/{username}')

    return render_template('add_note.html', form=form)

@app.route('/notes/<int:note_id>/update', methods=["GET","POST"])
def update_note(note_id):
    """Display update_note.html and updates if authenticated & authorized"""

    note = Note.query.get_or_404(note_id)

    if 'username' not in session:
        flash("You must be logged in!")
        return redirect("/login")
    elif session[SESSION_USERNAME] != note.owner:
        flash("Not your account!!")
        return redirect(f"/users/{session[SESSION_USERNAME]}")

    form = NoteForm(obj=note)

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{note.owner}')

    return render_template('update_note.html', note=note, form=form)

@app.route('/notes/<int:note_id>/delete', methods=["POST"])
def delete_note(note_id):
    """Delete user's note"""

    note = Note.query.get_or_404(note_id)

    if 'username' not in session:
        flash("You must be logged in!")
        return redirect("/login")
    elif session[SESSION_USERNAME] != note.owner:
        flash("Not your account!!")
        return redirect(f"/users/{session[SESSION_USERNAME]}")
    
    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(note)
        db.session.commit()

    return redirect(f"/users/{session[SESSION_USERNAME]}")