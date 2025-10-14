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
            max_length=128,
        ),
    ] = Field(...)
    phone_number: t.Annotated[
        str,
        StringConstraints(
            min_length=7,
            max_length=28,
        ),
    ] = Field(...)


class OrderId(BaseModel):
    id: t.Annotated[uuid.UUID, UUID4] = Field(...)


class OrderStatus(BaseModel):
    status: OrderStatusEnum = Field(...)
    detail: str = Field(...)
