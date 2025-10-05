from .order import OrderService

__all__ = (
    "get_order_service",
    "OrderService",
)


def get_order_service() -> OrderService:
    return OrderService()
