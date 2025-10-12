import logging

from fastapi import Request
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from ..config import Config
from ..db.base import AsyncDBSession
from ..db.models import User
from ..enums import Environment
from ..utils import verify_password

__all__ = ("AdminAuthenticationBackend",)

logger = logging.getLogger(__name__)


class AdminAuthenticationBackend:
    def __init__(self, config: Config):
        middlewares = [Middleware(SessionMiddleware, secret_key=config.secret_key),]
        if config.environment != Environment.LOCALHOST:
            middlewares.append(Middleware(ProxyHeadersMiddleware, trusted_hosts=["*"]),)
        self.middlewares = middlewares

    async def _get_db_user(self, username: str) -> User | None:
        async with AsyncDBSession() as session:
            try:
                return await session.get(User, username)
            except Exception as e:
                logger.error(f"An error occurred: {e}", stack_info=True)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username", "").strip()
        user: User | None = await self._get_db_user(username)
        if not (user and user.is_active):
            return False
        password = form.get("password", "")
        if verify_password(user.password, password):
            request.session.clear()
            request.session["user"] = user.username
            request.session["role"] = user.role
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "user" in request.session
