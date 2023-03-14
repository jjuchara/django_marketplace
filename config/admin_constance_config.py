"""File for storage static settings that we can change on admin page."""

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True
# CONSTANCE_DATABASE_CACHE_BACKEND = 'default'

CONSTANCE_ADDITIONAL_FIELDS = {
    "clear_site_cache": ["django.forms.fields.BooleanField", {"required": False}],
}

cache_time_keys = (
    "CATEGORY_CACHE_TIME",
    "CATALOG_CACHE_TIME",
    "BANNER_CACHE_TIME",
    "SELLER_CACHE_TIME",
    "SELLER_TOP_ITEM_CACHE_TIME",
    "TOP_ITEM_CACHE_TIME",
    "DETAIL_ITEM_CACHE_TIME",
)

cache_clear_keys = (
    "CLEAR_CATEGORY_CACHE",
    "CLEAR_BANNER_CACHE",
    "CLEAR_SELLER_CACHE",
    "CLEAR_CATALOG_CACHE",
    "CLEAR_SELLER_TOP_ITEM_CACHE",
    "CLEAR_TOP_ITEM_CACHE",
    "CLEAR_DETAIL_ITEM_CACHE",
    "CLEAR_SITE_CACHE",
)

CONSTANCE_CONFIG = (
    dict.fromkeys(cache_time_keys, (60 * 60 * 24, "Stored time in seconds"))
    | dict.fromkeys(
        cache_clear_keys,
        (False, "check and save to clear site cache", "clear_site_cache"),
    )
    | dict.fromkeys(
        ("ADMIN_SITE_HEADER",),
        ("Megano", "Admin site name. Need to restart server after change"),
    )
    | dict.fromkeys(
        ("ADMIN_SITE_TITLE",),
        ("Megano", "Admin site title. Need to restart server after change"),
    )
    | dict.fromkeys(("EXPRESS_DELIVERY_PRICE",), (500, "Express delivery price"))
    | dict.fromkeys(("FREE_DELIVERY_LIMIT",), (2000, "Free delivery limit"))
    | dict.fromkeys(("ORDINARY_DELIVERY_PRICE",), (200, "Ordinary delivery price"))
)

CONSTANCE_CONFIG_FIELDSETS = {
    "General Options": {
        "fields": (
            "ADMIN_SITE_HEADER",
            "ADMIN_SITE_TITLE",
        ),
        "collapse": True,
    },
    "Cache Options": (
        "CATEGORY_CACHE_TIME",
        "CLEAR_CATEGORY_CACHE",
        "CATALOG_CACHE_TIME",
        "CLEAR_CATALOG_CACHE",
        "BANNER_CACHE_TIME",
        "CLEAR_BANNER_CACHE",
        "SELLER_CACHE_TIME",
        "CLEAR_SELLER_CACHE",
        "SELLER_TOP_ITEM_CACHE_TIME",
        "CLEAR_SELLER_TOP_ITEM_CACHE",
        "TOP_ITEM_CACHE_TIME",
        "CLEAR_TOP_ITEM_CACHE",
        "DETAIL_ITEM_CACHE_TIME",
        "CLEAR_DETAIL_ITEM_CACHE",
        "CLEAR_SITE_CACHE",
    ),
    "Delivery Options": {
        "fields": (
            "EXPRESS_DELIVERY_PRICE",
            "ORDINARY_DELIVERY_PRICE",
            "FREE_DELIVERY_LIMIT",
        ),
        "collapse": True,
    },
}
