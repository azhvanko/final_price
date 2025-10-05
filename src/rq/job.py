from rq.job import Job
from sqlalchemy.orm import Session

__all__ = ("DBJob",)


class DBJob(Job):
    _db_session: Session | None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._db_session = None

    def attach_db_session(self, db_session: Session) -> None:
        self._db_session = db_session

    @property
    def db_session(self) -> Session:
        return self._db_session
