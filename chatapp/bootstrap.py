from future_router import Router
from flask import Blueprint, Flask

_ROUTERS: list[Router] = []

def push(router: Router):
    _ROUTERS.append(router)

def remove(router: Router):
    _ROUTERS.remove(router)

def init(app: Blueprint | Flask):
    for i in _ROUTERS:
        i.init_app(app)
