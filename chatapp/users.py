"""Users related modules"""

from re import compile as re_compile
from html import escape as html_escape
from flask_login import UserMixin
from .database import get_table

# from typing import NamedTuple

USERNAME_REGEX = re_compile(r"""[\[\[\]+=`~|}{'":;,<>/?!@#$%^&*()]+""")
userstb = get_table("users")
undefined = type("undefined", (object,), {"__repr__": lambda _: "undefined"})()

USABLE_COLUMNS = ("username", "display_name", "bio", "accept_tos", "email", "user_id")


def validate_username(username: str):
    """Validate username's structure"""
    return not bool(USERNAME_REGEX.findall(username))


def update_displayname(display_name: str):
    """Update display name"""
    return html_escape(display_name)


def parse_bio(bio: str):
    """Parse bio"""
    # TODO: Implement the function
    del bio
    return NotImplemented


class User(UserMixin):
    """User class for flask-login utility"""

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._data = kwargs

    @classmethod
    def get(cls, uid: str):
        """Get user by UID"""
        # print("users.py", uid)
        a = userstb.select_one({"user_id": uid}, only=USABLE_COLUMNS)
        if a:
            return cls(**a)
        raise ValueError(f"Unable to find uid {uid}")

    @property
    def id(self):
        """Return user's id"""
        return self.user_id

    @property
    def uid(self):
        """Return user's id"""
        return self.user_id

    def __getattr__(self, name: str):
        # print("User."+name, self._data)
        return self._data.get(name, undefined)

    def __repr__(self) -> str:
        return f"<User id={self.user_id}>"


__all__ = ["User", "validate_username", "update_displayname", "parse_bio"]
