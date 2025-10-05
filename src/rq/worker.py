import logging

from rq.queue import Queue
from rq.worker import SimpleWorker, WorkerStatus
from sqlalchemy import Engine
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)

from ..config import get_config
from ..db.base import create_db_engine
from .job import DBJob

__all__ = ("DBWorker",)

logger = logging.getLogger(__name__)


class DBWorker(SimpleWorker):
    _db_engine: Engine | None
    _db_session: Session | None

    def __init__(self, *args, **kwargs):
        kwargs["job_class"] = DBJob
        super().__init__(*args, **kwargs)
        self._db_engine = None
        self._db_session = None

    def work(self, *args, **kwargs):
        logger.info(f"Worker {self.name} starting up, initializing DB session")
        try:
            self._db_engine = create_db_engine(
                get_config(),
                {"application_name": f"rq_worker_{self.name}"},
            )
            self._db_session = sessionmaker(self._db_engine, expire_on_commit=False)()
            super().work(*args, **kwargs)
        finally:
            logger.info(f"Worker {self.name} shutting down, closing DB session")
            self._dispose_db_engine()

    def execute_job(self, job: DBJob, queue: Queue) -> None:
        self.prepare_execution(job)
        self.attach_db_session(job)
        self.perform_job(job, queue)
        self.set_state(WorkerStatus.IDLE)

    def attach_db_session(self, job: DBJob) -> None:
        job.attach_db_session(self._db_session)

    def _dispose_db_engine(self) -> None:
        if self._db_engine:
            self._db_engine.dispose()
            self._db_engine = None
            self._db_session = None
            logger.info("SQLAlchemy Engine disposed and resources cleared")
