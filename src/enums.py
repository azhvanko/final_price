import enum
import typing as t

__all__ = (
    "BaseEnum",
    "Environment",
    "OrderProcessingStatus",
    "OrderStatus",
)


class BaseEnum(enum.Enum):
    @classmethod
    def values(cls) -> tuple[t.Any, ...]:
        return tuple(member.value for member in cls)

    @classmethod
    def names(cls) -> tuple[str, ...]:
        return tuple(member.name for member in cls)

    @classmethod
    def choices(cls) -> tuple[tuple[str, t.Any], ...]:
        return tuple((member.value, member.name) for member in cls)


class Environment(str, BaseEnum):
    LOCALHOST = "LOCALHOST"
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"


class OrderStatus(str, BaseEnum):
    ACCEPTED = "ACCEPTED"
    ERROR = "ERROR"
    PROCESSING = "PROCESSING"
    REJECTED = "REJECTED"

    @property
    def description(self) -> str:
        match self:
            case self.ACCEPTED:
                return "Order has been accepted and queued"
            case self.ERROR:
                return "Unable to process order due to temporary error. Please try again later"
            case self.PROCESSING:
                return "Order is currently undergoing processing"
            case self.REJECTED:
                return "Order has been rejected due to invalid data"


class OrderProcessingStatus(str, BaseEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
