from typing import Iterable

from constance import config
from django.core.cache import cache
from django.db.models import QuerySet


def clear_all_cache() -> None:
    """
    The clear_all_cache function clears the cache of all its contents.

    :return: None
    """
    cache.clear()


def delete_cache(cache_key: str) -> None:
    """
    The delete_cache function deletes the cache file.

    :return: None
    """
    cache.delete(cache_key)


def add_to_cache(queryset: Iterable[QuerySet], cache_key: str) -> None:
    """
    The add_to_cache function accepts a queryset and a cache name.
    It then adds the queryset to the cache with the specified name,
    and also sets an expiration time of CATEGORY_CACHE_TIME seconds.

    :param queryset:Iterable[QuerySet]: Set the cache key to a list of objects
    :param cache_key:str: Identify the cache
    :return: None
    """
    cache.set(cache_key, queryset, config.CATEGORY_CACHE_TIME)
