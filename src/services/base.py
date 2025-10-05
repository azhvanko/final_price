import rq

from ..config import get_config, Config
from ..rq import get_rq_queue

__all__ = ("BaseService",)


class BaseService:
    config: Config
    rq_queue: rq.Queue

    def __init__(self) -> None:
        self.config = get_config()
        self.rq_queue = get_rq_queue(self.config)
