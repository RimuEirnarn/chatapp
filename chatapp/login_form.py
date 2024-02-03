from flask_login import UserMixin, LoginManager
from .database import users
from wtforms import BooleanField, StringField, PasswordField, Form, validators # type: ignore

login_manager = LoginManager()

class LoginForm(Form):
    username = StringField('username', [validators.DataRequired()])
    password = PasswordField('password', [
        validators.DataRequired(),
    ])
    remember = BooleanField('remember')

class RegistrationForm(Form):
    display_name = StringField('display_name', [validators.DataRequired()])
    username = StringField('username', [validators.DataRequired()])
    email = StringField('email', [validators.DataRequired()])
    password = PasswordField('password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password must match')
    ])
    confirm = PasswordField('confirm')
    accept_tos = BooleanField("tos_accept", [validators.DataRequired()])
    remember = BooleanField('remember')

class User(UserMixin):
    def get_id(self):
       return super().get_id()

@login_manager.user_loader
def load_user(uid: str): 
    return users.select_one({'uid': uid})
