import click

from .db import cli as db_cli

cli = click.CommandCollection(sources=[db_cli,])
