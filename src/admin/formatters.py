import typing as t
from datetime import datetime

from sqladmin.formatters import bool_formatter

__all__ = (
    "BASE_FORMATTERS",
    "datetime_formatter",
    "empty_formatter",
)


def datetime_formatter(value: datetime | None) -> str:
    return value.strftime("%d %B %Y, %H:%M:%S") if value else "-"


def empty_formatter(_: t.Any) -> str:
    return "-"


BASE_FORMATTERS: dict[type[t.Any], t.Callable[[t.Any], t.Any]] = {
    bool: bool_formatter,
    datetime: datetime_formatter,
    type(None): lambda _: "-",
}
