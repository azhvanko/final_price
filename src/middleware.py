import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from .config import Config
from .enums import Environment

__all__ = ("add_middlewares",)


def _create_cors_regex(host: str) -> str:
    return rf"https?://(.*\.)?{re.escape(host)}"


def add_middlewares(app: FastAPI, config: Config) -> None:
    if config.environment != Environment.LOCALHOST:
        # preferably handled by the reverse proxy (e.g., Nginx)
        app.add_middleware(
            CORSMiddleware,
            allow_origin_regex=_create_cors_regex(config.host.host),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        # potentially redundant behind a properly configured reverse proxy
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=[config.host.host, f"*.{config.host.host}"],
        )
        # fixes 'Mixed Content' errors when behind an HTTPS proxy.
        app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])  # TODO debug
