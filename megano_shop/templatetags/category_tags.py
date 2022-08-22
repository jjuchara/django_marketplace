from typing import Iterable

from django import template
from django.core.cache import cache
from django.db.models.query import QuerySet

from megano_shop.models import Category
from megano_shop.utils.cache_utils import add_to_cache

register = template.Library()


def change_category_active_flag(queryset: Iterable[QuerySet]) -> Iterable[QuerySet]:
    for category in queryset:
        if not category.is_leaf_node():
            category.is_active = (
                True if category.children.filter(item_category__status="a") else False
            )
            category.save()
        else:
            category.is_active = (
                True if category.item_category.filter(status="a") else False
            )
            category.save()
    return queryset


@register.inclusion_tag("megano_shop/category_list.html")
def get_categories():
    """Получаем все категории и проверяем их товары, если есть активные,
    то меняем флаг Category.is_active на True, в противном случае на False
    и возвращаем queryset"""
    categories_qs = cache.get("categories_qs")

    if categories_qs is not None:
        return {"object_list": categories_qs}

    categories = Category.objects.all().prefetch_related("item_category")
    categories = change_category_active_flag(categories).filter(is_active=True)
    add_to_cache(categories, cache_key="categories_qs")
    return {"object_list": categories}
