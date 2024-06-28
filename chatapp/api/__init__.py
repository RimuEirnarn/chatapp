"""API"""

from flask import Blueprint
from future_router import Router

API = Router(Blueprint("API", __name__, url_prefix="/api"))

__all__ = ["API"]
