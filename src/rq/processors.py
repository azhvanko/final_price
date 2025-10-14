import logging
import re
import typing as t

import phonenumbers
import regex
from rq import get_current_job
from rq.exceptions import InvalidJobOperation
from sqlalchemy.exc import IntegrityError

from ..db.models import Order
from ..enums import OrderProcessingStatus
from ..rq.job import DBJob

__all__ = ("process_order",)

logger = logging.getLogger(__name__)

PHONE_NUMBER_NON_DIGITS_RE_PATTERN = re.compile(r"\D")
PHONE_NUMBER_RE_PATTERN = re.compile(r"^\+?[\d() -]+$")
USER_NAME_RE_PATTERN = regex.compile(r"^[\p{L} '’-]+$")
WHITESPACES_RE_PATTERN = re.compile(r"\s+")


def _validate_user_name(user_name: str) -> tuple[bool, str | None, str | None]:
    user_name = WHITESPACES_RE_PATTERN.sub(" ", user_name.strip())
    if not USER_NAME_RE_PATTERN.match(user_name):
        return False, "User name contains invalid characters", None
    return True, None, user_name


def _validate_phone_number(phone_number: str) -> tuple[bool, str | None, str | None]:
    try:
        phone_number = WHITESPACES_RE_PATTERN.sub(" ", phone_number.strip())
        if not PHONE_NUMBER_RE_PATTERN.match(phone_number):
            return False, "Phone number contains invalid characters", None
        phone_digits = PHONE_NUMBER_NON_DIGITS_RE_PATTERN.sub("", phone_number)
        if not (7 <= len(phone_digits) <= 15):
            return False, "Phone number must contain between 7 and 15 digits", None
        if not phone_number.startswith("+"):
            phone_number = f"+{phone_number}"
        phone_obj = phonenumbers.parse(phone_number)
        if not (
                phonenumbers.is_possible_number(phone_obj)
                and phonenumbers.is_valid_number(phone_obj)
        ):
            return False, "Phone number is not valid", None
        normalized = phonenumbers.format_number(
            phone_obj,
            phonenumbers.PhoneNumberFormat.E164,
        )
        return True, None, normalized
    except phonenumbers.NumberParseException:
        return False, "Invalid phone number format", None
    except Exception as e:
        logger.error(
            f"Unexpected error validating phone number: {e}",
            exc_info=True,
            extra={"phone_number": phone_number},
        )
        return False, "Phone number is not valid", None


def process_order(order: dict) -> dict:
    validators: list[tuple[str, t.Callable[[str], tuple[bool, str | None, str | None]]]] = [
        ("user_name", _validate_user_name),
        ("phone_number", _validate_phone_number),
    ]
    normalized_fields: dict[str, str] = {}
    for field, validator in validators:
        is_valid, err_message, normalized_field = validator(order[field])
        if not is_valid:
            return {"status": OrderProcessingStatus.REJECTED, "detail": err_message}
        normalized_fields[field] = normalized_field
    rq_job: DBJob = get_current_job()
    if not rq_job:
        raise InvalidJobOperation("No job context found")
    _db_session = rq_job.db_session
    try:
        new_order = Order(
            id=rq_job.id,
            user_name=normalized_fields["user_name"],
            phone_number=normalized_fields["phone_number"],
        )
        _db_session.add(new_order)
        _db_session.commit()
    except IntegrityError:
        _db_session.rollback()
        return {
            "status": OrderProcessingStatus.REJECTED,
            "detail": "Phone number is already registered",
        }
    except Exception as e:
        logger.error(
            f"A database error occurred while creating order for job {rq_job.id}: {e}",
            exc_info=True,
        )
        _db_session.rollback()
        raise e
    return {"status": OrderProcessingStatus.ACCEPTED}
