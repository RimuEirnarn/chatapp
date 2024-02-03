from .database import users as userstb
from typing import NamedTuple
from re import compile as re_compile
from html import escape as html_escape

USERNAME_REGEX = re_compile(r'''[\[\[\]+=`~|}{'":;,<>/?!@#$%^&*()]+''')

def validate_username(username: str):
    return not bool(USERNAME_REGEX.findall(username))

def update_displayname(display_name: str):
    return html_escape(display_name)

def parse_bio(bio: str):
    ...

class UserData(NamedTuple):
    display_name: str = ""
    username: str = ''
    bio: str = ''
    email: str = ''
    password: str = ''

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        d = {}
        for key, value in data.items():
            if key in cls._fields:
                d[key] = value
        return cls(**d)

    @classmethod
    def from_db(cls, uid: str):
        user = userstb.select_one({'uid': uid})
        if not user:
            return cls()
        return cls.from_dict(user)
