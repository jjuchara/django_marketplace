import random
from collections import defaultdict
from typing import Any, Iterable

from django import template
from django.contrib.sessions.backends.db import SessionStore
from django.db.models import QuerySet

from megano_shop.models import Item
from megano_shop.services.compare import Compare

register = template.Library()


@register.simple_tag(name="compare_len")
def get_compare_items_quantity(session_obj: SessionStore) -> int:
    item_quantity = Compare.get_compare_items_quantity(
        compare_session_key="compare_items", session_obj=session_obj
    )
    return item_quantity


@register.simple_tag(name="compare_list")
def get_compare_items_list(session_obj: SessionStore) -> list["str"]:
    item_list = Compare.get_compare_list_items(
        compare_session_key="compare_items", session_obj=session_obj
    )
    return item_list


@register.inclusion_tag("megano_shop/compare_products.html")
def get_compare_products(session_obj: SessionStore, **kwargs) -> dict["str":Any]:
    items = Item.objects.filter(slug__in=session_obj["compare_items"])
    sorted_items = Compare.sort_by_add_to_list(items, session_obj, "compare_items")
    merged_spec = list()
    phrase = None

    if not kwargs.get("title_blank"):
        merged_spec = get_all_specifications(sorted_items)
        if not merged_spec:
            merged_spec = {}
            phrase = random.choice(phrases)

    return {
        "compare_list": sorted_items,
        "specifications": dict(merged_spec),
        "title_blank": kwargs.get("title_blank"),
        "name_main": kwargs.get("name_main"),
        "phrase": phrase,
    }


def get_all_specifications(item_list: Iterable[QuerySet]) -> dict[str:list] | None:
    merged_spec = defaultdict(list)
    for item in item_list:
        for spec_key, spec_value in item.specifications.items():
            merged_spec[spec_key].append([item.title, spec_value])

    if check_for_equal_spec(merged_spec, item_list):
        merged_spec = change_empty_value(merged_spec, item_list)
        return merged_spec
    return None


def change_empty_value(
    specifications: dict[str:list], items: Iterable[QuerySet]
) -> dict[str:list]:
    for k, v in specifications.items():
        if len(v) != len(items):
            value_to_compare = [item_title[0] for item_title in v]
            for pos, item in enumerate(items):
                if item.title not in value_to_compare:
                    specifications[k].insert(pos, [item.title, "-"])
    return specifications


def check_for_equal_spec(
    specification: dict, item_list: Iterable[QuerySet]
) -> dict[str:list]:
    common_spec = []
    if len(item_list) > 1:
        for k, v in specification.items():
            if len(v) > 1:
                common_spec.append(k)
        return True if len(common_spec) > 1 else False


phrases = (
    "Сравнивая себя с недостижимым идеалом совершенства, человек постоянно преисполняется чувством, что он"
    " ниже его, и мотивируется этим чувством.",
    "Сравнивая нашу Землю со Вселенной, мы находим, что она всего лишь точка.",
    "Разговоры о славе, чести, удовольствии и богатстве грязны по сравнению с любовью",
    "То, что мы говорим, ничто, по сравнению с тем, что мы чувствуем.",
)
