from .api import API
from . import direct_messageapi, groupchat_api 
from .bootstrap import push, init

del direct_messageapi, groupchat_api

push(API)

__all__ = ['init']
