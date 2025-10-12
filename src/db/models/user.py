from datetime import datetime

import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..base import DeclarativeBase
from ..enums import UserRole

__all__ = ("User",)


class User(DeclarativeBase):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        sqlalchemy.String(64),
        primary_key=True,
    )
    password: Mapped[str] = mapped_column(sqlalchemy.Text, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        sqlalchemy.Enum(UserRole, name="user_role_enum", create_type=True),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        sqlalchemy.Boolean,
        server_default=sqlalchemy.true(),
        nullable=False,
    )
    created: Mapped[datetime] = mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=func.now(),
    )
