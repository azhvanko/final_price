import logging

from sqlalchemy import delete

from .base import (
    DBEngine,
    DBSession,
    MetaData,
)
from .models import Order

__all__ = (
    "delete_all_orders",
    "init_db",
)

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


def init_db() -> None:
    MetaData.create_all(DBEngine)
