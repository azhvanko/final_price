import typing as t

import orjson
import structlog

__all__ = ("get_logging_config",)


def _orjson_serializer(obj: t.Any, **kwargs) -> str:
    return orjson.dumps(obj, **kwargs).decode("utf-8")


def get_logging_config(debug: bool = False) -> dict[str, t.Any]:
    def add_app_context(_, __, event_dict: dict[str, t.Any]) -> dict[str, t.Any]:
        # remove processors meta
        event_dict.pop("_from_structlog", None)
        event_dict.pop("_record", None)
        frame, _ = structlog._frames._find_first_app_frame_and_name(["logging", __name__])  # noqa
        event_dict["file"] = frame.f_code.co_filename
        event_dict["line"] = frame.f_lineno
        event_dict["function"] = frame.f_code.co_name
        return event_dict
    dev_processors = [structlog.processors.ExceptionPrettyPrinter(),] if debug else []
    processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        add_app_context,
        *dev_processors,
        structlog.processors.JSONRenderer(serializer=_orjson_serializer, option=orjson.OPT_SORT_KEYS),
    ]
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": processors,
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "DEBUG" if debug else "INFO",
            },
        },
    }
