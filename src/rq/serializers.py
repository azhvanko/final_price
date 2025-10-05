import typing as t

import orjson

__all__ = ("ORJSONSerializer",)


class ORJSONSerializer:
    @staticmethod
    def dumps(obj: t.Any) -> bytes:
        return orjson.dumps(obj, option=orjson.OPT_SERIALIZE_UUID)

    @staticmethod
    def loads(obj: bytes) -> t.Any:
        return orjson.loads(obj)
