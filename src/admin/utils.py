from fastapi import FastAPI
from sqladmin import Admin

from ..config import Config
from ..db.base import AsyncDBEngine, AsyncDBSession
from .auth import AdminAuthenticationBackend
from .models import (
    OrderAdmin,
    UserAdmin,
)

__all__ = ("register_admin_view",)


def register_admin_view(app: FastAPI, config: Config) -> None:
    admin = Admin(
        app,
        AsyncDBEngine,
        session_maker=AsyncDBSession,
        authentication_backend=AdminAuthenticationBackend(config),
    )
    admin.add_view(OrderAdmin)
    admin.add_view(UserAdmin)
