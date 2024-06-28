"""ChatApp utilities"""

from enum import IntFlag, auto, EJECT
from datetime import datetime
from functools import wraps
from typing import Callable, Mapping, NamedTuple, Any
from flask import jsonify, request
from flask_login import current_user
from flask_socketio import SocketIO, emit, rooms

MESSAGE_CHANNEL = "message_logs"


class ClientSession(NamedTuple):
    """Client session data

    Attributes:
    username: str
        The username of the client.
    display_name: str
        The display name of the client.
    rooms: tuple[str, ...]
        A tuple of rooms the client is currently in.
    current_room: str
        The room the client is currently in.
    socket_id: str
        The unique identifier for the client's socket connection.
    data: dict
        Additional data associated with the client's session."""

    username: str
    display_name: str
    rooms: tuple[str, ...]
    current_room: str
    socket_id: str
    data: dict


class UserPerm(IntFlag, boundary=EJECT):
    """User Permissions"""

    NO_PERM = 0
    BANNED = 0
    MEMBERS = auto()
    ADMIN = auto()
    OWNER = auto()


def http_message(status: str, msg: str, data: Any):
    """Send a API message"""
    return jsonify({"status": status, "message": msg, "data": data})


def http_info(msg: str, data: Any = None):
    """Sends info API message"""
    return http_message("info", msg, data)


def http_warning(msg: str, data: Any = None):
    """Sends warning API message"""
    return http_message("warning", msg, data)


def http_error(msg: str, data: Any = None):
    """Sends error API message"""
    return http_message("error", msg, data), 400


def http_success(msg: str, data: Any = None):
    """Sends a success API message"""
    return http_message("success", msg, data)


def socket_message(
    status: str, msg: str, data: Any, eid: int, room_id: str | None = None
):
    """Emit a message to MESSAGE_CHANNEL"""
    return emit(
        MESSAGE_CHANNEL,
        {"status": status, "message": msg, "data": data, "code": eid},
        to=room_id,
    )


def socket_info(msg: str, data: Any, eid: int, room_id: str | None = None):
    """Emit a info message to MESSAGE_CHANNEL"""
    return socket_message("info", msg, data, eid, room_id)


def socket_warning(msg: str, data: Any, eid: int, room_id: str | None = None):
    """Emit a warning message to MESSAGE_CHANNEL"""
    return socket_message("warning", msg, data, eid, room_id)


def socket_error(msg: str, data: Any, eid: int, room_id: str | None = None):
    """Emit a error message to MESSAGE_CHANNEL"""
    return socket_message("error", msg, data, eid, room_id)


def fabricate(app: SocketIO):
    """Setup an app and return a on_event function to help you"""

    def on_event(event_name: str):
        def outter(func: Callable):
            @app.on(event_name)
            @wraps(func)
            def wrapper(data: Mapping[str, Any]):
                data = dict(data)
                room = data.get("room", None)
                if room:
                    del data["room"]
                rooms_ = tuple(rooms()[1:])
                if room not in rooms_:
                    room = ""
                # print(type(current_user), current_user)
                session = ClientSession(
                    current_user.username,  # type: ignore
                    display_name=current_user.display_name,
                    rooms=rooms_,
                    current_room=room,
                    socket_id=request.sid,  # type: ignore
                    data=data,
                )
                print(session)
                return func(session)

            return wrapper

        return outter

    return on_event


def verify_room(room):
    """Verify room from user's assigned rooms."""
    rooms_ = rooms()
    return room in rooms_ and rooms_[0] != room


def validate_request(data: Mapping[str, Any]):
    """Validate any incoming events from user"""
    if not data.get("room", None):
        return False
    return None


def timestamp_now():
    """Returns current timestamp"""
    return datetime.now().timestamp()
