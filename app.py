import os

from flask import Flask, render_template, request, flash, redirect, session, g
import json
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from secrets import API_SECRET_KEY

from forms import UserAddForm, LoginForm, UserEditForm,UserRecipeSearchForm
from models import db, connect_db, User,Recipe,Likes,Fridge

CURR_USER_KEY = "curr_user"

app = Flask(__name__)



# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///myfridge'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


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
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect(f"/users/{user.id}")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
        return redirect(f"/users/{user.id}")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():  
    """Handle logout of user."""
    do_logout()

    flash("You have logged out","success")
    return redirect("/login")

@app.route('/users/<int:user_id>')
def show_user(user_id):
    """show users home page(logged in)"""

    
        
    user=User.query.get(user_id)

    recipes=(Recipe.query.filter(Recipe.user_id==user_id)
                    
                    .limit(100)
                    .all())
    likes=[recipes.id for recipe in user.likes]
    bio=user.bio

    return render_template('users/show_user.html',user=user,recipes=recipes,likes=likes,bio=bio)





@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user=g.user
    form=UserEditForm(obj=user)
 
    if form.validate_on_submit():
        if User.authenticate(user.username,form.password.data):
            user.username=form.username.data
            user.email=form.email.data
            user.image_url=form.image_url.data 
            
            db.session.commit()
            return redirect(f"/users/{user.id}")
        flash("wrong password, try again.", 'danger')
    return render_template('users/edit.html',form=form,user_id=user.id)




@app.route('/users/<int:user_id>/fridge',methods=["GET","POST"])
def show_fridge(user_id):
    """show the users fridge content"""

   

    user=User.query.get(user_id)


    return render_template('users/fridge.html',user=user)


@app.route('/recipe',methods=["GET"])
def get_recipe():
 
    ingredients=request.args["ingredients"]
    res=requests.get("https://api.spoonacular.com/recipes/findByIngredients?",
                        params={"apiKey":API_SECRET_KEY,"ingredients":ingredients,"number":6})
   
    data=res.json()
    
    return render_template("users/showrecipe.html",data=data)


@app.route('/recipe/<int:info_id>',methods=["GET"])
def show_recipe_info(info_id):

   
    #res=requests.get("https://api.spoonacular.com/recipes/716
   
    res=requests.get(f"https://api.spoonacular.com/recipes/{info_id}/information?includeNutrition=false",
                        params={"apiKey":API_SECRET_KEY})

    data=res.json()

  


    return render_template("individual.html",data=data)


@app.route('/recipe/<int:info_id>/analyzedInstructions',methods=["GET"])
def show_directions(info_id):
  
    res=requests.get(f"https://api.spoonacular.com/recipes/{info_id}/analyzedInstructions",
                            params={"apiKey":API_SECRET_KEY})

    instruction_data=res.json()
    

    return render_template("individual.html",instruction_data=instruction_data,user=g.user)

   
@app.route('/users/<int:user_id>/likes', methods=["GET"])
def show_likes(user_id):
    """ show user likes""" 
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('/users/likes.html', user=user, likes=g.user.likes)


@app.route('/users/<int:user_id>/home',methods=["GET"])
def show_user_home(user_id):
    """show users HOME page"""
    user=User.query.get_or_404(user_id)

    return render_template('/users/home.html',user=user)



#@app.route('/recipe/<int:info_id>/like', methods=['POST','GET'])
#def add_like(info_id):
    #"""Toggle a liked recipe for the currently-logged-in user."""

   # if not g.user:
       # flash("Access unauthorized.", "danger")
        #return redirect("/")

    #liked_recipe= Recipe.query.get_or_404(info_id)
    #if liked_recipe.user_id == g.user.id:
        #return abort(403)

    #user_likes = g.user.likes

    #if liked_recipe in user_likes:
        #g.user.likes = [like for like in user_likes if like != liked_recipe]
    #else:
        #g.user.likes.append(liked_recipe)

    #db.session.commit()

    #return redirect("/")



##
##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:"""
   
    return render_template("base.html")

##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
#https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
