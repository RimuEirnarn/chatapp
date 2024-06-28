"""Groupchat API"""

# pylint: disable=arguments-renamed
from enum import EJECT, IntFlag, auto
from flask import request
from flask_login import current_user
from future_router import ResourceDummy
from . import API  # pylint: disable=import-error
from ..utils import http_error, http_success, timestamp_now, UserPerm
from ..database import get_table
from ..rooms import generate_groupchat_id, identify_room

rooms = get_table("rooms")
users = get_table("users")
user_room_rel = get_table("user_room_relationship")
messages = get_table("messages")


def d_update(d1: dict, d2: dict):
    """Update dictionary"""
    nd = d1.copy()
    nd.update(d2)
    return nd


class Actions(IntFlag, boundary=EJECT):
    """Actions Enum"""

    BANNED = 0
    KICKED = auto()
    REDUCE_AS_MEMBER = auto()
    RAISED_AS_ADMIN = auto()
    RAISED_AS_OWNER = auto()


@API.resource("/gc", alias="gc")
class GroupChat(ResourceDummy):
    """Groupchat API"""

    @staticmethod
    def index():
        user_rels = user_room_rel.select({"user_id": current_user.uid})  # type: ignore
        groups = [
            d_update(rooms.select_one({"room_id": user_rooms.room_id}), user_rooms)
            for user_rooms in user_rels
        ]
        return http_success(
            "",
            data=tuple(
                (a for a in groups if identify_room(a["room_id"]) == "groupchat")
            ),
        )

    @staticmethod
    def store():  # type: ignore
        user_id = current_user.uid
        name = request.form.get("gc_name", None)

        if not name:
            return http_error("Name is empty")

        if not user_id:
            return http_error("Your ID cannot be found")

        if not users.select_one({"user_id": user_id}):
            return http_error("Your ID cannot be found")

        room_id = generate_groupchat_id(user_id)
        rooms.insert(
            {"room_id": room_id, "room_name": name, "created_at": timestamp_now()}
        )

        user_room_rel.insert(
            {"user_id": user_id, "room_id": room_id, "user_perm": UserPerm.OWNER}
        )

        return http_success("The GC is created", data={"gc_id": room_id})

    @staticmethod
    def destroy(room_id):  # type: ignore
        if identify_room(room_id) != "groupchat":
            return http_error("This is not a group chat!")

        room = rooms.select_one({"room_id": room_id})
        if not room:
            return http_error("No such room")

        user_rel = user_room_rel.select_one(
            {"room_id": room_id, "user_id": current_user.uid}
        )
        if not user_rel:
            return http_error("You are not a member of this group chat")

        if not user_rel.user_perm == UserPerm.OWNER:
            return http_error("You are not the group owner.")

        # Kick everyone from the group
        user_room_rel.delete({"room_id": room_id})

        # ... including the messages
        messages.delete({"room_id": room_id})
        return http_success("The group chat is permanently removed.")


@API.post("/gc/<room_id>/join")
def api_gc_join(room_id):
    """Join a group chat"""
    group = rooms.select_one({"room_id": room_id})
    if not group:
        return http_error("Group doesn't exists")

    user_rel = user_room_rel.select_one(
        {"room_id": room_id, "user_id": current_user.uid}
    )
    if user_rel:
        return http_error("You have already joined the group")

    user_room_rel.insert(
        {"room_id": room_id, "user_id": current_user.uid, "user_perm": UserPerm.MEMBERS}
    )
    return http_success("OK")


@API.delete("/gc/<room_id>/leave")
def api_gc_leave(room_id):
    """Leave a group chat"""
    group = rooms.select_one({"room_id": room_id})
    if not group:
        return http_error("Group doesn't exists")

    user_rel = user_room_rel.select_one(
        {"room_id": room_id, "user_id": current_user.uid}
    )
    if not user_rel:
        return http_error("You are not joined the group")

    if user_rel.user_perm == UserPerm.OWNER:
        return http_error(
            "You cannot leave your own group chat. Delegate to others first."
        )

    user_room_rel.delete_one({"room_id": room_id, "user_id": current_user.uid})
    return http_success("OK")


@API.patch("/gc/<room_id>/chperm/<uid>/<int:delegation>")
def api_gc_change_perm(
    room_id, uid, delegation: int
):  # pylint: disable=too-many-return-statements
    """Change a group member's permissions"""
    dele = Actions(delegation)
    group = rooms.select_one({"room_id": room_id})
    if not group:
        return http_error("Group doesn't exists")

    user_rel = user_room_rel.select_one(
        {"room_id": room_id, "user_id": current_user.uid}
    )
    if not user_rel:
        return http_error("You are not joined the group")

    target = user_room_rel.select_one({"room_id": room_id, "user_id": uid})

    if not target:
        return http_error("Targeted user doesn't joined the group")

    if not user_rel.user_perm in (UserPerm.OWNER, UserPerm.ADMIN):
        return http_error("Insufficent permission")

    if target.user_perm == UserPerm.OWNER and user_rel.user_perm == UserPerm.ADMIN:
        return http_error("Insufficent permission. Coup d'état is disabled.")

    # Python doesn't support switch-under-the-hood match, revert back to if-case

    if dele == Actions.REDUCE_AS_MEMBER:
        user_room_rel.update_one(
            {"room_id": room_id, "user_id": uid, "user_perm": UserPerm.MEMBERS}
        )
        return http_success("Reduced the target into member")

    if dele == Actions.BANNED:
        user_room_rel.update_one(
            {"room_id": room_id, "user_id": uid, "user_perm": UserPerm.BANNED}
        )
        return http_success("Banned the users")

    if dele == Actions.KICKED:
        user_room_rel.delete_one({"room_id": room_id, "user_id": uid})
        return http_success("Kicked the user")

    if dele == Actions.RAISED_AS_ADMIN and target.user_perm != UserPerm.ADMIN:
        user_room_rel.update_one(
            {"room_id": room_id, "user_id": uid, "user_perm": UserPerm.ADMIN}
        )
        return http_success("Raised the target into admin")

    if dele == Actions.RAISED_AS_ADMIN:
        return http_success("No-op, target is already an ADMIN.")

    if dele == Actions.RAISED_AS_OWNER:
        user_room_rel.update_one(
            {"room_id": room_id, "user_id": uid, "user_perm": UserPerm.OWNER}
        )
        user_room_rel.update_one(
            {
                "room_id": room_id,
                "user_id": current_user.uid,
                "user_perm": target.user_perm,
            }
        )
        return http_success("Raised the target into owner")

    return http_error("Actions key doesn't match.")
