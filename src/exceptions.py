import http
import typing as t

from typing_extensions import Doc

__all__ = ("HTTPException",)


# starlette.exceptions.HTTPException
class HTTPException(Exception):
    def __init__(
        self,
        status_code: t.Annotated[
            int,
            Doc(
                """
                HTTP status code to send to the client.
                """
            ),
        ],
        detail: t.Annotated[
            t.Any,
            Doc(
                """
                Any data to be sent to the client in the `detail` key of the JSON
                response.
                """
            ),
        ] = None,
        headers: t.Annotated[
            dict[str, str] | None,
            Doc(
                """
                Any headers to send to the client in the response.
                """
            ),
        ] = None,
    ):
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

    def __str__(self) -> str:
        return f"{self.status_code}: {self.detail}"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"
