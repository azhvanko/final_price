import logging

import phonenumbers
from rq import get_current_job
from rq.exceptions import InvalidJobOperation
from sqlalchemy.exc import IntegrityError

from ..db.models import Order
from ..enums import OrderProcessingStatus
from ..rq.job import DBJob

__all__ = ("process_order",)

logger = logging.getLogger(__name__)


def _validate_phone_number(phone_number: str) -> tuple[bool, str | None, str | None]:
    try:
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
    except phonenumbers.NumberParseException as e:
        return False, f"Invalid phone number format: {str(e)}", None
    except Exception as e:
        logger.error(
            f"Unexpected error validating phone number: {e}",
            exc_info=True,
            extra={"phone_number": phone_number},
        )
        return False, "Phone number is not valid", None


def process_order(order: dict) -> dict:
    _is_valid, err_message, phone_number = _validate_phone_number(order["phone_number"])
    if not _is_valid:
        return {"status": OrderProcessingStatus.REJECTED, "detail": err_message}
    rq_job: DBJob = get_current_job()
    if not rq_job:
        raise InvalidJobOperation("No job context found")
    _db_session = rq_job.db_session
    try:
        new_order = Order(
            id=rq_job.id,
            user_name=order["user_name"],
            phone_number=phone_number,
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
