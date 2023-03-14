from decimal import Decimal

from constance import config
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    """Model for Category with nasted tree"""

    title = models.CharField(max_length=60, unique=True, verbose_name=_("Category"))
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Parent category"),
    )
    slug = models.SlugField()
    is_active = models.BooleanField(verbose_name=_("Is active"), default=False)
    icon = models.ImageField(
        upload_to="img/category_icons", verbose_name=_("Icon"), blank=True, null=True
    )
    discount = models.ManyToManyField(
        to="Discounts", blank=True, verbose_name=_("Discount")
    )

    class MPTTMeta:
        order_insertion_by = ["title"]

    class Meta:
        unique_together = [["parent", "slug"]]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    @admin.display(description="Icon_preview")
    def icon_prev(self):
        return mark_safe(f'<img src="{self.icon.url}" width="100"/>')

    def get_absolute_url(self):
        return reverse("filtered_category", kwargs={"path": self.get_path()})

    def __str__(self):
        return self.title


class Tags(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Tag"))

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name


class Images(models.Model):
    image = models.ImageField(upload_to="items", blank=True, verbose_name=_("Image"))

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")


class Item(models.Model):
    """Model for Item"""

    STATUS_CHOICES = [
        ("a", "Active"),
        ("i", "Inactive"),
    ]

    category = TreeForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="item_category",
        verbose_name=_("Category"),
    )
    slug = models.SlugField(verbose_name=_("slug"))
    tag = models.ManyToManyField(
        Tags, blank=True, related_name="tag_item", verbose_name=_("Tag")
    )
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    main_image = models.ImageField(
        upload_to="img/item_images/%Y/%m/%d/", blank=True, verbose_name=_("Main image")
    )
    discount = models.ManyToManyField(
        "Discounts", blank=True, related_name="item", verbose_name=_("Discount")
    )
    images = models.ManyToManyField(Images, blank=True, verbose_name=_("Images"))
    description = models.TextField(max_length=1000, verbose_name=_("Description"))
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default="a", verbose_name=_("Status")
    )
    specifications = models.JSONField(
        verbose_name=_("Specifications"), blank=True, null=True
    )
    count_view = models.IntegerField(default=0, verbose_name=_("count view"))

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")

    def get_absolute_url(self):
        return reverse("items_list", args=[str(self.slug)])

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title


class Banner(models.Model):
    """Model for Banners"""

    image = models.ImageField(
        upload_to="images/%Y/%m/%d/", blank=True, verbose_name=_("Banner image")
    )
    link = models.URLField(max_length=200, verbose_name=_("URL"))
    title = models.CharField(max_length=17, verbose_name=_("Title"))
    description = models.TextField(max_length=300, verbose_name=_("Description"))
    is_active = models.BooleanField(default=False, verbose_name=_("Status"))

    class Meta:
        # verbose_name = "Banner"
        verbose_name_plural = _("Banners")

    def get_absolute_url(self):
        pass

    def __str__(self):
        return self.link


class Reviews(models.Model):
    """Reviews model"""

    created_on = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Creation date")
    )
    edited_on = models.DateTimeField(auto_now=True, verbose_name=_("Updating date"))
    user = models.ForeignKey(
        to=User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name="review_user",
    )
    item = models.ForeignKey(
        to=Item,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Item"),
        related_name="review_item",
    )
    content = models.TextField(
        max_length=3000, blank=True, verbose_name=_("Review text")
    )

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")

    def __str__(self):
        if User.is_authenticated:
            return str(self.user)
        else:
            return _("Guest")


class Discounts(models.Model):
    """Model for Discount"""

    TYPE = [
        ("p", _("Promo code")),
        ("d", _("Discount")),
    ]

    AMOUNT_CHOICE = [("cashed", _("Fixed amount")), ("percentage", _("Percentage"))]

    title = models.CharField(max_length=200, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    image = models.ImageField(
        upload_to="images/%Y/%m/%d/promo/", blank=True, verbose_name=_("Promo image")
    )
    discount_weight = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(10), MinValueValidator(1)],
        verbose_name=_("Discount weight"),
    )
    discount_type = models.CharField(
        max_length=1, choices=TYPE, default="d", verbose_name=_("Discount type")
    )
    amount_type = models.CharField(
        max_length=10,
        choices=AMOUNT_CHOICE,
        default="cashed",
        verbose_name=_("Amount type"),
    )
    amount = models.PositiveIntegerField(
        default=0, verbose_name=_("Discount"), blank=True, null=True
    )
    promo_code = models.CharField(
        max_length=50, verbose_name=_("Promo code text"), blank=True, null=True
    )
    items_qty = models.PositiveIntegerField(
        default=0, validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    starts_on = models.DateTimeField(blank=True, verbose_name=_("Starts on"), null=True)
    ends_on = models.DateTimeField(blank=True, verbose_name=_("Ends on"), null=True)
    is_active = models.BooleanField(default=False, verbose_name=_("Activity"))

    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")

    def __str__(self):
        return self.title


class AppliedDiscounts(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name="user_applied_discount",
    )
    discount = models.ForeignKey(
        to=Discounts,
        on_delete=models.CASCADE,
        verbose_name=_("Discount"),
        related_name="applied_discount",
    )

    class Meta:
        db_table = "megano_shop_applied_discounts"
        verbose_name = _("Applied Discount")
        verbose_name_plural = _("Applied Discounts")


class Stock(models.Model):
    """Model for Stock"""

    item = models.ForeignKey(
        Item,
        blank=True,
        on_delete=models.CASCADE,
        related_name="stock_item",
        verbose_name=_("Item"),
    )
    seller = models.ForeignKey(
        User, blank=True, on_delete=models.PROTECT, verbose_name=_("Seller")
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name=_("Quantity"))
    discount = models.ForeignKey(
        Discounts,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Discount"),
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name=_("Price")
    )
    count_view = models.IntegerField(default=0, verbose_name=_("count view"))
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("Created on"))

    class Meta:
        verbose_name = _("Stock")
        verbose_name_plural = _("Stocks")

    def __str__(self):
        return self.seller.username

    @property
    def get_category(self):
        return self.item.category


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ("o", _("Open")),
        ("c", _("Closed")),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("p", _("Payed")),
        ("u", _("Not paid")),
    ]
    DELIVERY_CHOICE = (
        ("ordinary", _("Ordinary delivery")),
        ("express", _("Express delivery")),
    )
    PAYMENT_CHOICE = (
        ("online_card", _("Online")),
        ("online_account", _("Online from random person's account")),
    )
    order_number = models.CharField(
        max_length=6, unique=True, verbose_name=_("Order number")
    )
    buyer = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="order_buyer",
        verbose_name=_("Customer"),
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name=_("Total amount")
    )
    payment_method = models.CharField(
        max_length=60,
        choices=PAYMENT_CHOICE,
        default="online_card",
        verbose_name=_("Payment method"),
    )
    shipping_type = models.CharField(
        max_length=250,
        choices=DELIVERY_CHOICE,
        default="ordinary",
        verbose_name=_("Delivery"),
    )
    payment_status = models.CharField(
        max_length=60,
        choices=PAYMENT_STATUS_CHOICES,
        default="u",
        verbose_name=_("Payment status"),
    )
    order_status = models.CharField(
        max_length=60,
        choices=ORDER_STATUS_CHOICES,
        default="o",
        verbose_name=_("Order status"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created on"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated on"))

    def __str__(self):
        return self.order_number

    @property
    def calculate_price_with_ship(self):
        shipping_price = self.total_price
        if self.shipping_type == "express":
            shipping_price += Decimal(config.EXPRESS_DELIVERY_PRICE)
        elif self.shipping_type == "ordinary":
            items_stock = set()
            for item in self.cart.all():
                items_stock.add(item.stock.seller.username)
            if self.total_price < config.FREE_DELIVERY_LIMIT or len(items_stock) > 1:
                shipping_price += Decimal(config.ORDINARY_DELIVERY_PRICE)
        return shipping_price

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")


class OrderCart(models.Model):
    order = models.ForeignKey(
        to=Order, on_delete=models.CASCADE, related_name="cart", verbose_name=_("Order")
    )
    stock = models.ForeignKey(
        to=Stock,
        on_delete=models.CASCADE,
        related_name="order_cart",
        verbose_name=_("Stock"),
    )
    item = models.ForeignKey(
        to=Item, on_delete=models.CASCADE, related_name="cart", verbose_name=_("Item")
    )
    items_price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name=_("Item cost"), default=0
    )
    items_qty = models.PositiveIntegerField(verbose_name=_("Items quantity"), default=0)
    total_price = models.DecimalField(
        max_digits=9, decimal_places=2, default=0, verbose_name=_("Total amount")
    )

    def __str__(self):
        return str(self.order.order_number)

    class Meta:
        verbose_name = _("Order cart")
        verbose_name_plural = _("Order carts")


class Views(models.Model):
    """User's view model"""

    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Created on"))
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="view_user",
        verbose_name=_("Customer"),
    )
    item = models.ForeignKey(
        to=Item,
        blank=True,
        on_delete=models.CASCADE,
        related_name="view_item",
        verbose_name=_("Item"),
    )

    def __str__(self):
        return str(self.item)

    class Meta:
        verbose_name = _("View")
        verbose_name_plural = _("Views")
