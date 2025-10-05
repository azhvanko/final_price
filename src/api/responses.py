from fastapi import status
from pydantic import (
    BaseModel,
    Field,
)


class ValidationErrorResponse(BaseModel):
    detail: str = Field(...)
    errors: dict[str, str] = Field(...)


VALIDATION_ERROR_RESPONSE = {status.HTTP_400_BAD_REQUEST: {"model": ValidationErrorResponse}}
