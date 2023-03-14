from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "last_name", "role", "user"]
    list_filter = ["role"]
    # search_fields = []
    actions = ["mark_as_customer", "mark_as_seller"]

    def mark_as_customer(self, request, queryset):
        queryset.update(role="customer")

    def mark_as_seller(self, request, queryset):
        queryset.update(role="seller")

    mark_as_customer.short_description = _("Mark as Customer")
    mark_as_seller.short_description = _("Mark as Seller")
