from django.db.models import Avg, Count, Min
from django.utils.translation import gettext_lazy as _

from account.models import Profile
from megano_shop.models import Item


def sellers_list():
    sellers_set = ()
    try:
        sellers = Profile.objects.filter(role="seller")
        for seller in sellers:
            sellers_set = (*sellers_set, (seller.user_id, seller.name))
    except Exception:
        pass
    return sellers_set


def manufacturers_list():
    manufacturers_names = set()
    try:
        items = Item.objects.all()
        for item in items:
            manufacturer = item.specifications["manufacturer"]
            manufacturers_names.add(manufacturer)
        names = list(manufacturers_names)
        names.sort()
        manufacturers = ()
        for name in names:
            manufacturers = (*manufacturers, (name, name))
        return manufacturers
    except Exception:
        return ["", ""]


availability_choices = free_delivery_choices = (
    ("1", _("yes")),
    ("0", _("no")),
    ("", _("no matter")),
)


def form_cleaned_data_filters(form_cleaned_data):
    filters = dict()
    if form_cleaned_data["price_min"]:
        filters["stock_item__price__gte"] = form_cleaned_data["price_min"]
    if form_cleaned_data["price_max"]:
        filters["stock_item__price__lte"] = form_cleaned_data["price_max"]
    if form_cleaned_data["title"]:
        filters["title__contains"] = form_cleaned_data["title"]
    if form_cleaned_data["manufacturer"]:
        filters["specifications__manufacturer__in"] = form_cleaned_data["manufacturer"]
    if form_cleaned_data["seller"]:
        filters["stock_item__seller_id__in"] = form_cleaned_data["seller"]
    if form_cleaned_data["available"] == "1":
        filters["stock_item__quantity__gt"] = 0
    if form_cleaned_data["available"] == "0":
        filters["stock_item__quantity__lte"] = 0
    return filters


def form_cleaned_data_sorting(form_cleaned_data, items):
    if form_cleaned_data["sorting_order"] == "cheap_first":
        items = items.annotate(avg_price=Avg("stock_item__price")).order_by("avg_price")
    elif form_cleaned_data["sorting_order"] == "expensive_first":
        items = items.annotate(avg_price=Avg("stock_item__price")).order_by(
            "-avg_price"
        )
    elif form_cleaned_data["sorting_order"] == "popular_first":
        items = items.annotate(reviews=Count("review_item")).order_by("-reviews")
    elif form_cleaned_data["sorting_order"] == "not_popular_first":
        items = items.annotate(reviews=Count("review_item")).order_by("reviews")
    elif form_cleaned_data["sorting_order"] == "new_first":
        items = items.annotate(new=Min("stock_item__created_on")).order_by("new")
    elif form_cleaned_data["sorting_order"] == "old_first":
        items = items.annotate(new=Min("stock_item__created_on")).order_by("-new")
    return items
