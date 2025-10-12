import logging

from sqlalchemy import delete

from ..base import DBSession
from ..models import Order

__all__ = ("delete_all_orders",)

logger = logging.getLogger(__name__)


def delete_all_orders() -> None:
    with DBSession() as session:
        try:
            session.execute(delete(Order))
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"An error occurred: {e}", stack_info=True)
            raise
