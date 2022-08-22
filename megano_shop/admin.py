from constance import config
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django_mptt_admin.admin import DjangoMpttAdmin

from .models import (
    AppliedDiscounts,
    Banner,
    Category,
    Discounts,
    Images,
    Item,
    Order,
    OrderCart,
    Reviews,
    Stock,
    Tags,
    Views,
)


class ItemsDiscountInline(admin.TabularInline):
    model = Item.discount.through
    extra = 1

    verbose_name = _("Item")
    verbose_name_plural = _("Items")


class CategoryDiscountInline(admin.TabularInline):
    model = Category.discount.through
    extra = 1
    verbose_name = _("Category")
    verbose_name_plural = _("Categories")


class CategoryAdmin(DjangoMpttAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "slug", "parent", "icon_prev", "is_active")
    readonly_fields = ("icon_prev",)
    list_editable = ("is_active",)
    list_filter = ("is_active", "title")
    exclude = ("discount",)

    inlines = [CategoryDiscountInline]


admin.site.register(Category, CategoryAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_number",
        "buyer",
        "payment_method",
        "shipping_type",
        "payment_status",
        "order_status",
        "created_at",
        "updated_at",
    )
    list_filter = ("order_number", "buyer")


admin.site.register(Order, OrderAdmin)


class OrderCartAdmin(admin.ModelAdmin):
    list_display = ("order", "stock", "item", "items_price", "items_qty", "total_price")


admin.site.register(OrderCart, OrderCartAdmin)


class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("id", "title", "category", "description", "status", "count_view")
    list_display_links = ("id", "title")
    search_fields = ("title", "price")
    list_filter = ("category", "status")
    list_editable = ("status",)
    fields = (
        "images",
        "title",
        "description",
        "category",
        "slug",
        "main_image",
        "specifications",
        "status",
        "tag",
        "count_view",
    )
    inlines = [ItemsDiscountInline]
    exclude = ("discount",)

    actions = ["mark_as_active", "mark_as_inactive"]

    def mark_as_active(self, request, queryset):
        queryset.update(status="a")

    def mark_as_inactive(self, request, queryset):
        queryset.update(status="i")

    mark_as_active.short_description = _("Mark as active")
    mark_as_inactive.short_description = _("Mark as inactive")


admin.site.register(Item, ItemAdmin)


class BannerAdmin(admin.ModelAdmin):
    list_display = ("id", "link")
    list_filter = ("is_active",)
    fields = ("title", "link", "image", "description", "is_active")


admin.site.register(Banner, BannerAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "user", "created_on", "edited_on")
    list_filter = ("item", "user", "created_on", "edited_on")
    search_fields = (
        "item",
        "user",
    )
    readonly_fields = ("created_on", "edited_on")
    fields = ("user", "item", "created_on", "edited_on", "content")


admin.site.register(Reviews, ReviewAdmin)


class StockAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "seller", "price", "quantity", "get_category")
    list_filter = ("seller", "item", "item__category")
    fields = ("item", "seller", "price", "quantity")
    list_editable = ("quantity", "price")

    # def get_items(self, obj):
    #     return "\n".join([item.title for item in obj.item.all()])


admin.site.register(Stock, StockAdmin)


class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "is_active",
        "title",
        "discount_weight",
        "discount_type",
        "amount",
        "starts_on",
        "ends_on",
    )
    fields = (
        "is_active",
        "discount_type",
        "title",
        "description",
        "discount_weight",
        "amount_type",
        "amount",
        "promo_code",
        "items_qty",
        "image",
        "starts_on",
        "ends_on",
    )

    list_editable = ("is_active",)

    inlines = [ItemsDiscountInline, CategoryDiscountInline]

    def get_readonly_fields(self, request, obj=None):
        read_only_field = super(DiscountAdmin, self).get_readonly_fields(request)
        if obj and obj.discount_type == "d":
            read_only_field = ("promo_code", "items_qty")
        return read_only_field


admin.site.register(Discounts, DiscountAdmin)


class AppliedDiscountAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "discount")
    fields = ("user", "discount")


admin.site.register(AppliedDiscounts, AppliedDiscountAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    fields = ("name",)


admin.site.register(Tags, TagAdmin)


class ImagesAdmin(admin.ModelAdmin):
    list_display = ("id",)
    fields = ("image",)


admin.site.register(Images, ImagesAdmin)


class ViewsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date")
    fields = ("user", "item")


admin.site.register(Views, ViewsAdmin)

AdminSite.site_header = config.ADMIN_SITE_HEADER
AdminSite.site_title = config.ADMIN_SITE_TITLE
