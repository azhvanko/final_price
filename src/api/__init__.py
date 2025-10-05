from fastapi import (
    APIRouter,
    Response,
    status,
)
from fastapi.responses import ORJSONResponse

from .routers import orders_router

health_router = APIRouter(include_in_schema=False)


@health_router.get("/health", status_code=status.HTTP_200_OK)
def health() -> Response:
    return Response()


router = APIRouter(default_response_class=ORJSONResponse)
router.include_router(health_router)
router.include_router(orders_router, prefix="/api")
