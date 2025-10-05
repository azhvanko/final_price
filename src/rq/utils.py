import logging

import redis
import rq
from redis.exceptions import ConnectionError

from ..config import Config
from .serializers import ORJSONSerializer

__all__ = (
    "get_rq_queue",
    "shutdown_redis_resources",
    "startup_redis_resources",
)

logger = logging.getLogger(__name__)


_REDIS_CLIENT: redis.Redis | None = None
_RQ_QUEUE: rq.Queue | None = None


def _initialize_redis_resources(config: Config) -> None:
    global _REDIS_CLIENT, _RQ_QUEUE
    redis_dsn = config.redis_dsn.unicode_string()
    try:
        redis_client = redis.Redis.from_url(redis_dsn)
        redis_client.ping()
        _REDIS_CLIENT = redis_client
        _RQ_QUEUE = rq.Queue(
            name=config.rq_queue_name,
            connection=_REDIS_CLIENT,
            serializer=ORJSONSerializer,
        )
        logger.info("Successfully established Redis connection and RQ Queue")
    except ConnectionError as e:
        logger.error(f"Failed to connect to Redis at {redis_dsn}: {e}")
        _REDIS_CLIENT = None
        _RQ_QUEUE = None


def get_rq_queue(config: Config) -> rq.Queue:
    global _RQ_QUEUE
    if _RQ_QUEUE is None:
        _initialize_redis_resources(config)
    return _RQ_QUEUE


def startup_redis_resources(config: Config) -> None:
    global _REDIS_CLIENT, _RQ_QUEUE
    logger.info("Initializing Redis connection and create RQ queue")
    _initialize_redis_resources(config)
    if _REDIS_CLIENT is None or _RQ_QUEUE is None:
        raise RuntimeError("Failed to initialize Redis resources")


def shutdown_redis_resources() -> None:
    global _REDIS_CLIENT, _RQ_QUEUE
    logger.info("Closing Redis connection")
    if _REDIS_CLIENT:
        _REDIS_CLIENT.close()
        _REDIS_CLIENT = None
    if _RQ_QUEUE:
        _RQ_QUEUE = None
