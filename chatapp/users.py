from flask_login import UserMixin
from .database import get_table
from typing import NamedTuple
from re import compile as re_compile
from html import escape as html_escape

USERNAME_REGEX = re_compile(r'''[\[\[\]+=`~|}{'":;,<>/?!@#$%^&*()]+''')
userstb = get_table('users')
undefined = type('undefined', (object,), {'__repr__': lambda _: 'undefined'})()

USABLE_COLUMNS = ('username', 'display_name', 'bio', 'accept_tos', 'email', 'user_id')

def validate_username(username: str):
    return not bool(USERNAME_REGEX.findall(username))

def update_displayname(display_name: str):
    return html_escape(display_name)

def parse_bio(bio: str):
    ...

class User(UserMixin):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        print('User.__init__()', kwargs)
        self._data = kwargs

    @classmethod
    def get(cls, uid: str):
        #print("users.py", uid)
        a = userstb.select_one({'user_id': uid}, only=USABLE_COLUMNS)
        if a:
            return cls(**a)
        raise ValueError(f"Unable to find uid {uid}")

    @property
    def id(self):
        return self.user_id

    def __getattr__(self, name: str):
        #print("User."+name, self._data)
        return self._data.get(name, undefined)

    def __repr__(self) -> str:
        return f"<User id={self.user_id}>"
