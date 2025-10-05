import typing as t
import uuid

from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    UUID4,
)

from ..enums import OrderStatus as OrderStatusEnum

__all__ = (
    "Order",
    "OrderId",
    "OrderStatus",
)


class Order(BaseModel):
    user_name: t.Annotated[
        str,
        StringConstraints(
            min_length=2,
            strip_whitespace=True,
            pattern=r"^[a-zA-Zа-яА-ЯёЁ\s'’‑-]+$",
        ),
    ] = Field(...)
    phone_number: t.Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=7,
            max_length=28,
            pattern=r"^\+?[0-9()\- ]+$",
        ),
    ] = Field(...)


class OrderId(BaseModel):
    id: t.Annotated[uuid.UUID, UUID4] = Field(...)


class OrderStatus(BaseModel):
    status: OrderStatusEnum = Field(...)
    detail: str = Field(...)
