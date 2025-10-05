# https://python-rq.org/docs/workers/#using-a-config-file
from ..config import get_config
from ..logging import get_logging_config


DICT_CONFIG = get_logging_config(get_config().debug)
