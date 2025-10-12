from sqladmin import ModelView
from sqladmin.filters import (
    BooleanFilter,
    StaticValuesFilter,
)
from starlette.requests import Request
from wtforms.fields import TextAreaField

from ..db.enums import (
    OrderStatus,
    UserRole,
)
from ..db.models import (
    Order,
    User,
)
from ..utils import hash_password
from .formatters import BASE_FORMATTERS

__all__ = (
    "OrderAdmin",
    "UserAdmin",
)


class OrderAdmin(ModelView, model=Order):
    can_create = False
    can_delete = False
    column_default_sort = ("created", True)
    column_filters = [StaticValuesFilter(Order.status, list(OrderStatus.choices())),]
    column_list = [
        Order.id,
        Order.user_name,
        Order.phone_number,
        Order.status,
        Order.notes,
        Order.created,
    ]
    column_searchable_list = [
        Order.user_name,
        Order.phone_number,
    ]
    column_type_formatters = BASE_FORMATTERS
    form_edit_rules = [
        "user_name",
        "phone_number",
        "status",
        "notes",
    ]
    form_overrides = {"notes": TextAreaField,}
    name_plural = "Orders"
    page_size = 100
    page_size_options = [25, 50, 100, 200]


class UserAdmin(ModelView, model=User):
    column_default_sort = ("username", False)
    column_filters = [
        BooleanFilter(User.is_active, "Active"),
        StaticValuesFilter(User.role, list(UserRole.choices()), "User role"),
    ]
    column_list = [
        User.username,
        User.role,
        User.is_active,
        User.created,
    ]
    column_searchable_list = [User.username,]
    column_type_formatters = BASE_FORMATTERS
    form_create_rules = [
        "username",
        "password",
        "role",
        "is_active",
    ]
    form_edit_rules = [
        "username",
        "password",
        "role",
        "is_active",
    ]
    form_include_pk = True
    name_plural = "Users"
    page_size = 100
    page_size_options = [25, 50, 100, 200]

    def is_visible(self, request: Request) -> bool:
        role: UserRole | None = request.session.get("role", None)
        return role == UserRole.ADMIN

    def is_accessible(self, request: Request) -> bool:
        role: UserRole | None = request.session.get("role", None)
        return role == UserRole.ADMIN

    async def on_model_change(
        self,
        data: dict,
        model: User,
        is_created: bool,
        request: Request,
    ) -> None:
        if is_created:
            data["password"] = hash_password(data["password"])
        else:
            if data["password"] != model.password:
                data["password"] = hash_password(data["password"])
