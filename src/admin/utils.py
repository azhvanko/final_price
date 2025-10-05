from fastapi import FastAPI
from sqladmin import Admin

from ..config import Config
from ..db.base import DBEngine, DBSession
from .auth import AdminAuthenticationBackend
from .models import OrderAdmin

__all__ = ("register_admin_view",)


def register_admin_view(app: FastAPI, config: Config) -> None:
    admin = Admin(
        app,
        DBEngine,
        session_maker=DBSession,
        authentication_backend=AdminAuthenticationBackend(config),
    )
    admin.add_view(OrderAdmin)
