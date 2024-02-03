from flask import request
from flask_login import current_user
from future_router import ResourceDummy
from .api import API
from .utils import http_error, http_success, timestamp_now
from .database import rooms, users, user_room_relationship
from .rooms import generate_groupchat_id, identify_room

@API.resource("/gc", alias='gc')
class GroupChat(ResourceDummy):
    @staticmethod
    def store(): # type: ignore
        user_id = current_user.uid
        name = request.form.get('gc_name', None)

        if not name:
            return http_error("Name is empty")

        if not user_id:
            return http_error("Your ID cannot be found")

        if not users.select_one({'user_id': user_id}):
            return http_error("Your ID cannot be found")

        room_id = generate_groupchat_id(user_id)
        rooms.insert({'room_id': room_id, 'room_name': name, 'created_at': timestamp_now()})

        user_room_relationship.insert({'user_id': user_id, 'room_id': room_id})
    
        return http_success("The GC is created", data={'gc_id': room_id})

    @staticmethod
    def destroy(room_id): # type: ignore
        if identify_room(room_id) != 'groupchat':
            return http_error("This is not a group chat!")
        
        group = rooms.select_one({'room_id': room_id})
        user = user_room_relationship.select_one({'room_id': room_id, 'user_id': current_user.uid})

