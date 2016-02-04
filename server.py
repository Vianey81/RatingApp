"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from sqlalchemy import func
from model import User, Rating, Movie, connect_to_db, db
import correlation

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

    movies = Movie.query.order_by('title').all()
    return render_template("movie_list.html", movies=movies)

@app.route('/users')
def user_list():
    """Show list of all users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/sign_up')
def sign_up():
    """Form to sign in as a user"""

    return render_template("register.html")

@app.route('/register_user', methods=["POST"])
def register_user():
    """Verify the user and if it is doesn't exist Add it to the DB."""

    # Get the fields for the form

    email = request.form.get("email")
    password = request.form.get("password")

    user = db.session.query(User).filter_by(email=email).all()

    if user != []:
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
        return redirect("/login")
    

    return redirect("/sign_up")

@app.route('/logout')
def logout():
    """Log out a signed user"""

    session.pop('user_id', None)
    flash("User logged out succesfully.")
    return redirect("/")

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
            user_id = user[0].user_id
            flash("User logged in succesfully!.")
            if 'user_id' not in session:
                session['user_id'] = [user_id]
            return redirect("/user_info/"+str(user_id))
        else:
            flash("User or Password incorrect!.")
    else:
        flash("The user doesn't exist in the System.")


    return redirect("/sign_user")

@app.route("/user_info/<int:user_id>")
def user_info(user_id):
    """Show the info of a user"""
    user = db.session.query(User).filter_by(user_id=user_id).one()
    ratings = db.session.query(Rating).filter_by(user_id=user_id).all()
    print user
    print ratings
    return render_template("form_user.html", 
                            user=user,
                            ratings=ratings)

@app.route("/movie_info/<int:movie_id>")
def movie_info(movie_id):
    """Show the info of a particular movie"""
    #Get the object Movie
    movie = Movie.query.get(movie_id)
    
    #Get the id of the user in the session and its ratings.
    if 'user_id' in session:
        user_id = session["user_id"][0]   
        user_rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        # Prediction code: only predict if the user hasn't rated it.
        if (not user_rating) and user_id:
            user = User.query.get(user_id)
            if user:
                prediction = user.predict_rating(movie)
        else:
            prediction = None
    else:
        user_rating = None

        prediction = None 

    # Get average rating of movie

    rating_scores = [r.score for r in movie.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)
    ratings = Rating.query.filter_by(movie_id=movie_id).all()
    return render_template("form_movie.html", 
                            movie=movie,
                            user_rating=user_rating,
                            average=avg_rating,
                            prediction=prediction,
                            ratings=ratings)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
