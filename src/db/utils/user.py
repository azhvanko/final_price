import logging

from sqlalchemy import insert

from ...config import get_config
from ...utils import hash_password
from ..base import DBSession
from ..enums import UserRole
from ..models import User

__all__ = (
    "create_default_users",
    "create_user",
)

logger = logging.getLogger(__name__)


def create_default_users() -> None:
    config = get_config()
    create_user(config.default_admin_username, config.default_admin_password, UserRole.ADMIN)
    create_user(config.default_user_username, config.default_user_password, UserRole.USER)


def create_user(username: str, password: str, role: UserRole) -> None:
    with DBSession() as session:
        try:
            hashed_password = hash_password(password)
            session.execute(
                insert(User).values(username=username, password=hashed_password, role=role)
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"An error occurred: {e}", stack_info=True)
            raise
