from sqladmin import ModelView
from sqladmin.filters import StaticValuesFilter

from ..db.enums import OrderStatus
from ..db.models import Order
from .formatters import BASE_FORMATTERS

__all__ = ("OrderAdmin",)


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
    form_excluded_columns = [
        Order.id,
        Order.created,
    ]
    name_plural = "Orders"
    page_size = 100
    page_size_options = [25, 50, 100, 200]
