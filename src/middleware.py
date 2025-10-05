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
    # CORS
    if config.environment != Environment.LOCALHOST:
        cors_kwargs = {"allow_origin_regex": _create_cors_regex(config.host.host)}
    else:
        cors_kwargs = {"allow_origins": ["*"]}
    app.add_middleware(
        CORSMiddleware,
        **cors_kwargs,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # trusted hosts
    if config.environment != Environment.LOCALHOST:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=[config.host.host, f"*.{config.host.host}"],
        )
        app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])  # TODO debug
