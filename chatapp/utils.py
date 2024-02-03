from datetime import datetime
from functools import wraps
from typing import Callable, Mapping, NamedTuple, Any
from flask import jsonify, request
from flask_login import current_user
from flask_socketio import SocketIO, emit, rooms, send

MESSAGE_CHANNEL = "message_logs"

class ClientSession(NamedTuple):
    username: str
    rooms: tuple[str, ...]
    current_room: str
    socket_id: str
    data: dict

def http_message(status: str, msg: str, data: Any):
    """Send a API message"""
    return jsonify({'status': status, 'message': msg, 'data': data})

def http_info(msg: str, data: Any = None):
    return http_message('info', msg, data)

def http_warning(msg: str, data: Any = None):
    return http_message('warning', msg, data)

def http_error(msg: str, data: Any = None):
    return http_message('error', msg, data), 400

def http_success(msg: str, data: Any = None):
    return http_message('success', msg, data)

def socket_message(status: str, msg: str, data: Any, eid: int, roomID: str | None = None):
    """Emit a message to MESSAGE_CHANNEL"""
    return emit(MESSAGE_CHANNEL, {'status': status, 'message': msg, 'data': data, 'code': eid}, to=roomID)

def socket_info(msg: str, data: Any, eid: int, roomID: str | None = None):
    """Emit a info message to MESSAGE_CHANNEL"""
    return socket_message("info", msg, data, eid, roomID)

def socket_warning(msg: str, data: Any, eid: int, roomID: str | None = None):
    """Emit a warning message to MESSAGE_CHANNEL"""
    return socket_message("warning", msg, data, eid, roomID)

def socket_error(msg: str, data: Any, eid: int, roomID: str | None = None):
    """Emit a error message to MESSAGE_CHANNEL"""
    return socket_message("error", msg, data, eid, roomID)

def fabricate(app: SocketIO):
    """Setup an app and return a on_event function to help you"""
    def on_event(event_name: str):
        def outter(func: Callable):
            @app.on(event_name)
            @wraps(func)
            def wrapper(data: Mapping[str, Any]):
                data = dict(data)
                room = data.get('room', None)
                if room:
                    del data['room']
                rooms_ = tuple(rooms()[1:])
                if room not in rooms_:
                    room = ''
                session = ClientSession("username",
                                        rooms=rooms_,
                                        current_room=room,
                                        socket_id=request.sid, # type: ignore
                                        data=data)
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
    if not data.get('room', None):
        return False

def timestamp_now():
    return datetime.now().timestamp()
