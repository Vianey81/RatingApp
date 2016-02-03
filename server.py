"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from sqlalchemy import func
from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/movies')
def movie_list():
    """Show list of all movies."""

    movies = Movie.query.all()
    return render_template("movie_list.html", movies=movies)

@app.route('/users')
def user_list():
    """Show list of all users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/sign_user')
def sign_user():
    """Form to sign in as a user"""

    return render_template("sign-in.html")

@app.route('/verify_user', methods=["POST"])
def verify_user():
    """Verify the user and if it is doesn't exist Add it to the DB."""

    # Get the fields for the form

    email = request.form.get("email")
    password = request.form.get("password")

    user = db.session.query(User).filter_by(email=email).all()

    if user != None:
        user_id = user[0].user_id
        flash("The user already exist.")
    else:
        user = User(email=email,
                password=password,
                )
        # We need to add to the session or it won't ever be stored
        db.session.add(user)
        # Once we're done, we should commit our work
        db.session.commit()
        flash("User succesfully added!.")
        user_id = db.session.query(func.max(User.user_id)).one()
    

    return redirect("/sign_user")

@app.route('/login')
def login():
    """Form to sign in as a user"""

    return render_template("form_login.html")

@app.route('/verify_login', methods=["POST"])
def verify_login():
    """Login the user."""

    # Get the fields for the form
    email = request.form.get("email")
    password = request.form.get("password")
    user = db.session.query(User).filter_by(email=email).all()

    if len(user) > 0:
        if ((user[0].password == password) and (user[0].email == email)): 
            flash("User logged in succesfully!.")
            if 'user_id' not in session:
                session['user_id'] = [user_id]
            return redirect("/")
        else:
            flash("User or Password incorrect!.")
    else:
        flash("The user doesn't exist in the System.")


    return redirect("/sign_user")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
