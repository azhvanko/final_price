import typing as t
import uuid

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Path,
    status,
)
from pydantic import UUID4

from ...schemas import (
    Order,
    OrderId,
    OrderStatus,
)
from ...services import (
    get_order_service,
    OrderService,
)
from ..responses import VALIDATION_ERROR_RESPONSE

ORDER_BODY = t.Annotated[
    Order,
    Body(
        description="Order body",
        example={
            "user_name": "John Doe",
            "phone_number": "+375 29 111-11-11",
        },
    ),
]
ORDER_ID_PATH = t.Annotated[
    uuid.UUID,
    UUID4,
    Path(
        description="Order id",
        example=uuid.uuid4(),
    ),
]


orders_router = APIRouter(prefix="/orders", tags=["orders",],)


@orders_router.post(
    "/",
    response_model=OrderId,
    responses=VALIDATION_ERROR_RESPONSE,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    payload: ORDER_BODY,
    order_service: OrderService = Depends(get_order_service),
) -> OrderId:
    return order_service.create_order(payload)


@orders_router.get(
    "/{order_id}/status",
    response_model=OrderStatus,
    responses=VALIDATION_ERROR_RESPONSE,
    status_code=status.HTTP_200_OK,
)
def get_order_status(
    order_id: ORDER_ID_PATH,
    order_service: OrderService = Depends(get_order_service),
) -> OrderStatus:
    return order_service.get_order_status(order_id)
