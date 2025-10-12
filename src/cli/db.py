import click

from ..db.enums import UserRole
from ..db.utils import (
    create_default_users as _create_default_users,
    create_user as _create_user,
    delete_all_orders as _delete_all_orders,
)


@click.group()
def cli() -> None:
    pass


@cli.command("create_default_users")
def create_default_users() -> None:
    _create_default_users()


@cli.command("create_user")
@click.option("-u", "--username", type=str, required=True)
@click.option("-p", "--password", type=str, required=True)
@click.option("-r", "--role", type=click.Choice(UserRole), required=True)
def create_user(username: str, password: str, role: UserRole) -> None:
    _create_user(username, password, role)


@cli.command("delete_all_orders")
def delete_all_orders() -> None:
    _delete_all_orders()
