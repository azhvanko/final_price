import hashlib
import hmac
import os

from fastapi import Request
from sqladmin.authentication import AuthenticationBackend

from ..config import Config

__all__ = ("AdminAuthenticationBackend",)


class AdminAuthenticationBackend(AuthenticationBackend):  # TODO
    _iterations: int
    _salt: bytes
    _admin_username: bytes
    _admin_password: bytes

    def __init__(self, config: Config):
        super().__init__(config.secret_key)
        self._iterations = 128_000
        self._salt = os.urandom(16)
        self._admin_username = config.admin_username.encode()
        self._admin_password = self._pbkdf2(config.admin_password, self._salt)

    def _pbkdf2(self, password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            self._iterations,
        )

    def _verify_password(self, provided: str) -> bool:
        candidate = self._pbkdf2(provided, self._salt)
        return hmac.compare_digest(candidate, self._admin_password)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username", "").strip()
        password = form.get("password", "")
        user_ok = hmac.compare_digest(username.encode(), self._admin_username)
        password_ok = self._verify_password(password)
        if user_ok and password_ok:
            request.session.clear()
            request.session["authenticated_user"] = username
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "authenticated_user" in request.session
