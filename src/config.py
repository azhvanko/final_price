from functools import cache, cached_property
from pathlib import Path

from pydantic import (
    computed_field,
    Field,
    PostgresDsn,
    RedisDsn,
)
from pydantic_settings import BaseSettings

from .enums import Environment

__all__ = (
    "Config",
    "get_config",
)


class Config(BaseSettings):
    # Project
    debug: bool = Field(default=False)
    environment: Environment = Field(...)
    secret_key: str = Field(...)
    default_admin_username: str = Field(...)
    default_admin_password: str = Field(...)
    default_user_username: str = Field(...)
    default_user_password: str = Field(...)
    # Postgres
    postgres_dsn: PostgresDsn = Field(...)
    # Redis / RQ
    redis_dsn: RedisDsn = Field(...)
    rq_queue_name: str = Field(...)
    rq_job_retry: bool = Field(default=False)
    rq_job_retry_count: int = Field(default=3, ge=1)
    rq_job_timeout: int = Field(default=60, ge=5)  # 1 m.
    rq_job_result_ttl: int = Field(default=60 * 5, ge=60)  # 5 m.
    rq_job_failure_ttl: int = Field(default=60 * 60, ge=60 * 5)  # 1 h.

    @computed_field
    @cached_property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @computed_field
    @cached_property
    def static_dir(self) -> Path:
        return self.base_dir / "data" / "static"

    @computed_field
    @cached_property
    def assets_dir(self) -> Path:
        return self.static_dir / "assets"


@cache
def get_config() -> Config:
    return Config()
