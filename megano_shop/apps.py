from django.apps import AppConfig


class MeganoShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "megano_shop"

    def ready(self):
        pass
