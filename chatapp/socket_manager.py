from json import dumps as parse
from flask_socketio import SocketIO, send, join_room, leave_room

from chatapp.utils import ClientSession, fabricate

socketio = SocketIO()
on_event = fabricate(socketio)

@on_event('message')
def on_message(session: ClientSession):
    if session.current_room:
        socketio.emit('message',
                      {'text': f"[{session.username}] {session.data.get('message', '<no message>')}"},
                      to=session.current_room)

@socketio.on('join_gc')
def on_join_room(data):
    # TODO: join_room may notify other users
    room = data.get('room', None)
    if not room:
        send(parse({'text': 'no'}))
        return
    join_room(room)
    socketio.emit('message', {'text': f'[{room}] user joined this room'}, to=room)

@socketio.on("")

@socketio.on('leave_gc')
def on_leave_room(data):
    room = data.get('room', None)
    if not room:
        send(parse({'text': 'no'}))
        return
    leave_room(room)
    socketio.emit('message', {'text': f"[{room}] user has left the chat"}, to=room)
