"""Socket manager"""

from json import dumps as parse
from time import time
from flask_login import current_user
from flask_socketio import SocketIO, send, join_room, leave_room
from chatapp.database import get_table
from chatapp.utils import ClientSession, UserPerm, fabricate

user_room_relationship = get_table("user_room_relationship")
socketio = SocketIO()
on_event = fabricate(socketio)


@on_event("message")
def on_message(session: ClientSession):
    """On message event"""
    if session.current_room and session.data.get("message"):
        socketio.emit(
            "message",
            {
                "text": session.data.get("message", "<no message>"),
                "username": session.username,
                "display_name": session.display_name,
                "time": time(),
                "msg_type": "user",
            },
            to=session.current_room,
        )


@socketio.on("join_gc")
def on_join_room(data):
    """On join room event"""
    room = data.get("room", None)
    if not room:
        send(parse({"text": "no"}))
        return
    if not user_room_relationship.select_one(
        {"room_id": room, "user_id": current_user.id}
    ):
        user_room_relationship.insert(
            {"room_id": room, "user_id": current_user.id, "user_perm": UserPerm.MEMBERS}
        )
        join_room(room)
        socketio.emit(
            "message",
            {
                "text": f"[{room}] user joined this room",
                "time": time(),
                "msg_type": "system",
            },
            to=room,
        )


@socketio.on("connect")
def on_connect():
    """On connect event"""
    if current_user.is_authenticated:
        user_rels = user_room_relationship.select(
            {"user_id": current_user.uid}, only=("room_id",), squash=True
        )
        for i in user_rels["room_id"]:
            join_room(i)


@socketio.on("disconnect")
def on_disconnect():
    """On disconnect event"""
    if current_user.is_authenticated:
        user_rels = user_room_relationship.select(
            {"user_id": current_user.uid}, only=("room_id",), squash=True
        )
        for i in user_rels["room_id"]:
            try:
                leave_room(i)
            except Exception:  # pylint: disable=broad-exception-caught
                pass


@socketio.on("leave_gc")
def on_leave_room(data):
    """On leave room event"""
    room = data.get("room", None)
    if not room:
        send(parse({"text": "no"}))
        return
    user_rel = user_room_relationship.select_one(
        {"room_id": room, "user_id": current_user.uid}
    )
    if user_rel["user_perm"] == UserPerm.BANNED:
        send(parse({"text": "You cannot leave when you are banned"}))
        return
    leave_room(room)
    user_room_relationship.delete_one({"room_id": room, "user_id": current_user.uid})
