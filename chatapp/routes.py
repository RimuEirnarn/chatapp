"""Routes"""

# pylint: disable=import-error

from .api import direct_messageapi
from .api import API
from .api import groupchat_api
from .bootstrap import push, init

del direct_messageapi, groupchat_api

push(API)

__all__ = ["init"]
