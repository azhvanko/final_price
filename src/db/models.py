import uuid
from datetime import datetime

import sqlalchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import DeclarativeBase
from .enums import OrderStatus

__all__ = ("Order",)


class Order(DeclarativeBase):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
    )
    user_name: Mapped[str] = mapped_column(sqlalchemy.String(256))
    phone_number: Mapped[str] = mapped_column(sqlalchemy.String(32), nullable=False, unique=True)
    status: Mapped[OrderStatus] = mapped_column(
        sqlalchemy.Enum(OrderStatus, name="order_status_enum", create_type=True),
        nullable=False,
        default=OrderStatus.PENDING,
    )
    notes: Mapped[str | None] = mapped_column(sqlalchemy.Text, nullable=True)
    created: Mapped[datetime] = mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=func.now(),
    )
