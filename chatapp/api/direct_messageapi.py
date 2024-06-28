"""DM API Reference"""

from flask import request
from flask_login import current_user
from future_router import ResourceDummy
from . import API
from ..utils import http_error, http_success, timestamp_now
from ..database import get_table
from ..rooms import generate_direct_message_id

rooms = get_table("rooms")
users = get_table("users")
user_room_rel = get_table("user_room_relationship")


@API.resource("/dm", alias="dm")
class DirectMessage(ResourceDummy):
    """DM API Reference"""

    @staticmethod
    def store():  # type: ignore
        user_id = current_user.uid
        target = request.form.get("target_id", None)

        if not user_id:
            return http_error("Your ID cannot be found")

        if not target:
            return http_error("Target ID cannot be found")

        if not users.select_one({"user_id": user_id}):
            return http_error("Your ID cannot be found")

        if not users.select_one({"user_id": target}):
            return http_error("Target ID cannot be found")

        room_id = generate_direct_message_id(user_id, target)
        rooms.insert(
            {
                "room_id": room_id,
                "room_name": f"DM {user_id} and {target}",
                "created_at": timestamp_now(),
            }
        )

        user_room_rel.insert({"user_id": user_id, "room_id": room_id})
        user_room_rel.insert({"user_id": target, "room_id": room_id})

        return http_success("The DM is created", data={"dm_id": room_id})
