"""Database module"""

from uuid import UUID
from atexit import register
from sqlite_database import Database, real, text, integer
from sqlite_database.functions import Function
from werkzeug.security import generate_password_hash

count = Function("COUNT")

FIRST_TIME = False
database = Database("db.sqlite3")


def initialized():
    """Is the database initialized?"""
    try:
        return bool(database.table("users").select())
    except Exception:  # pylint: disable=broad-exception-caught
        return False


def init():
    """Initialize the database"""
    print("Database initializing")
    userstb = database.create_table(
        "users",
        [
            text("display_name"),
            text("username").unique(),
            text("email"),
            real("created_at"),
            text("user_id").primary(),
            text("bio").default(""),
            text(
                "password"
            ).allow_null(),  # Assuming you'd have a hashed password field
            integer("accept_tos").default(1),
        ],
    )

    database.create_table(
        "rooms",
        [
            text("room_name"),
            text("room_id").primary(),
            real("created_at"),
        ],
    )

    database.create_table(
        "user_room_relationship",
        [
            text("user_id").foreign("users/user_id"),
            text("room_id").foreign("rooms/room_id"),
            text("user_perm").default(None),
        ],
    )

    m = database.create_table(
        "messages",
        [
            text("content"),
            text("user_id").foreign("users/user_id"),
            text("room_id").foreign("rooms/room_id"),
            text("message_id").primary(),
            real("timestamp"),
            text("reply_to").foreign("messages/message_id").default("undefined"),
        ],
    )

    database.sql.commit()

    m.insert(
        {
            "content": "\0",
            "user_id": "undefined",
            "room_id": "undefined",
            "message_id": "undefined",
            "timestamp": 0,
        }
    )

    userstb.insert(
        {
            "display_name": "SYSTEM",
            "username": "system",
            "password": "",
            "email": "system@localhost",
            "created_at": 0.0,
            "user_id": str(UUID(int=0)),
        }
    )

    userstb.insert(
        {
            "display_name": "test",
            "username": "test",
            "password": generate_password_hash("admin"),
            "email": "system@localhost",
            "created_at": 0.0,
            "user_id": str(UUID(int=1000)),
        }
    )
    database.sql.commit()


if not initialized():
    init()
    FIRST_TIME = True

users = database.table("users")
rooms = database.table("rooms")
user_room_relationship = database.table("user_room_relationship")
messages = database.table("messages")
get_table = database.table


def database_close():
    """Close database connection"""
    print("Database closed")
    database.sql.commit()
    database.close()


register(database_close)
