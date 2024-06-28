"""Bootstrap"""

# pylint: disable=unused-import

from future_router import Router
from flask import Blueprint, Flask

# Bootstrap required APIs
import chatapp.api.message_api

# ===

_ROUTERS: list[Router] = []


def push(router: Router):
    """Push a new router"""
    _ROUTERS.append(router)


def remove(router: Router):
    """Remove a router"""
    _ROUTERS.remove(router)


def init(app: Blueprint | Flask):
    """Initialize the app"""
    for i in _ROUTERS:
        i.init_app(app)
