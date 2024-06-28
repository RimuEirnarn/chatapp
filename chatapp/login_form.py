"""Login forms"""

from flask_login import LoginManager
from wtforms import BooleanField, StringField, PasswordField, Form, validators  # type: ignore
from .users import User

login_manager = LoginManager()


class LoginForm(Form):
    """Login forms"""

    username = StringField("username", [validators.DataRequired()])
    password = PasswordField(
        "password",
        [
            validators.DataRequired(),
        ],
    )
    remember = BooleanField("remember")


class RegistrationForm(Form):
    """Registration forms"""

    display_name = StringField("display_name", [validators.DataRequired()])
    username = StringField("username", [validators.DataRequired()])
    email = StringField("email", [validators.DataRequired()])
    password = PasswordField(
        "password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Password must match"),
        ],
    )
    confirm = PasswordField("confirm")
    accept_tos = BooleanField("tos_accept", [validators.DataRequired()])
    remember = BooleanField("remember")


@login_manager.user_loader
def load_user(uid: str):
    """Load user by UID"""
    # print("login_form.py", uid)
    return User.get(uid)
