import orjson
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import (
    DeclarativeBase as _DeclarativeBase,
    Session,
    sessionmaker,
)
from sqlalchemy.pool import SingletonThreadPool

from ..config import (
    Config,
    get_config,
)

__all__ = (
    "create_db_engine",
    "DBEngine",
    "DBSession",
    "DeclarativeBase",
    "MetaData",
)


class DeclarativeBase(_DeclarativeBase):
    pass


def create_db_engine(config: Config, connect_args: dict | None = None) -> Engine:
    return create_engine(
        config.postgres_dsn.unicode_string(),
        echo=config.debug,
        poolclass=SingletonThreadPool,
        pool_pre_ping=True,
        json_deserializer=lambda o: orjson.loads(o),
        json_serializer=lambda o: orjson.dumps(o),
        connect_args=connect_args or {},
    )


MetaData = DeclarativeBase.metadata
DBEngine = create_db_engine(get_config())
DBSession: sessionmaker[Session] = sessionmaker(DBEngine, expire_on_commit=False)
