from ..enums import BaseEnum

__all__ = ("OrderStatus",)


class OrderStatus(str, BaseEnum):
    CANCELED = "CANCELED"
    CONFIRMED = "CONFIRMED"
    PENDING = "PENDING"

    @property
    def description(self) -> str:
        match self:
            case self.CANCELED:
                return "Order has been canceled"
            case self.CONFIRMED:
                return "Order has been confirmed and accepted for processing"
            case self.PENDING:
                return "Order is pending confirmation"
