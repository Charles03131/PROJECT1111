from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length



class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    bio=TextAreaField('(Optional) Bio')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])



class UserEditForm(FlaskForm):
    """Form for Editing user."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    bio=TextAreaField('(Optional)bio')


################# FORMS FOR USERS ACCOUNT/PAGE #####################

#class AddToFridgeForm(FlaskForm):
   # """Form to add items to the users fridge"""

class UserRecipeSearchForm(FlaskForm):
    """form for searching for recipes"""

    ingredients=StringField('Ingredients',validators=[DataRequired()])