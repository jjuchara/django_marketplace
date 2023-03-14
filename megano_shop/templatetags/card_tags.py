from django import template
from django.db.models import Avg

from megano_shop.models import Item, Stock

from ..services.discounts import DiscountsService

register = template.Library()


@register.simple_tag()
def get_average_price(item_id):
    items = (Item.objects.get(id=item_id),)
    discount = DiscountsService.get_priority_discount(items)
    if not discount:
        average_price = Stock.objects.filter(item_id=item_id).aggregate(Avg("price"))[
            "price__avg"
        ]
        return average_price
    average_price = Stock.objects.filter(item_id=item_id).aggregate(Avg("price"))[
        "price__avg"
    ]
    average_price = DiscountsService.calculate_price_with_discount(
        price=average_price, discount=discount
    )
    return average_price


@register.simple_tag(takes_context=True)
def url_replace(context, field, value):
    dict_ = context["request"].GET.copy()
    dict_[field] = value
    return dict_.urlencode()
