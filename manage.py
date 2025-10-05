from logging.config import dictConfig

from src.cli import cli
from src.config import get_config
from src.logging import get_logging_config


if __name__ == "__main__":
    dictConfig(get_logging_config(get_config()))
    cli()
