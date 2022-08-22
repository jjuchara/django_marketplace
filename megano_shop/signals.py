from enum import Enum

from constance.signals import config_updated
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Category, Item
from .utils.cache_utils import clear_all_cache, delete_cache


class CacheTypeKeys(Enum):
    """Объект для хранения ключей из config, и названия кэшей"""

    CLEAR_CATEGORY_CACHE = "categories_qs"
    CLEAR_CATALOG_CACHE = "cached_items_by_category"
    CLEAR_SELLER_CACHE = "name_of_your_cache_1"
    CLEAR_SELLER_TOP_ITEM_CACHE = "name_of_your_cache_2"
    CLEAR_BANNER_CACHE = "name_of_your_cache_3"
    CLEAR_TOP_ITEM_CACHE = "name_of_your_cache_4"
    CLEAR_DETAIL_ITEM_CACHE = "name_of_your_cache_6"
    CLEAR_SITE_CACHE = ""


@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Item)
def invalidate_cache(sender, instance, **kwargs):
    if sender == Category:
        delete_cache("categories_qs")
    else:
        delete_cache(instance.category.title)
        delete_cache("categories_qs")


@receiver(config_updated)
def admin_cache_clear_by_type(sender, key, old_value, new_value, **kwargs):
    if key == "CLEAR_SITE_CACHE" and new_value:
        clear_all_cache()
        setattr(sender, key, old_value)
    else:
        for cache_type in CacheTypeKeys:
            if cache_type.name is key and new_value and key != "CLEAR_SITE_CACHE":
                delete_cache(cache_type.value)
                setattr(sender, key, old_value)
