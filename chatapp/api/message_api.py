"""Message API"""

# pylint: disable=arguments-renamed
from flask_login import current_user
from sqlite_database.signature import op
from . import API  # pylint: disable=import-error
from ..utils import UserPerm, http_success
from ..database import get_table

user_room_rel = get_table("user_room_relationship")
messages = get_table("messages")


@API.get("/messages")
def index_messages():
    """Retrieve all messages"""
    uid = current_user.uid

    message = []
    group_rels = user_room_rel.select(
        {"user_id": uid, "user_perm": op != UserPerm.BANNED}, only=("room_id",)
    )
    for i in group_rels:
        message.append(messages.select({"room_id": i["room_id"]}))

    return http_success("oke", {"data": message})
