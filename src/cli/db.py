import click

from ..db.utils import (
    delete_all_orders as _delete_all_orders,
    init_db as _init_db,
)


@click.group()
def cli() -> None:
    pass


@cli.command("delete_all_orders")
def init_db() -> None:
    _delete_all_orders()


@cli.command("init_db")
def init_db() -> None:
    _init_db()
