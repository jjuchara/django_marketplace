from typing import Tuple

from django.db.models import Max
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from cart.cart import Cart
from megano_shop.models import Discounts, Item, Stock


class DiscountsService:
    @classmethod
    def get_all_discounts(cls, items: QuerySet | Tuple[Item]) -> QuerySet:
        """get and return all discounts for one item or list of items"""
        discount = Discounts.objects.prefetch_related("item").filter(
            item__in=items, is_active=True
        )
        return discount

    @classmethod
    def get_priority_discount(cls, items: QuerySet | Tuple[Item]) -> Discounts:
        """get max weight of discounts queryset and return queryset with max discount weight"""
        max_rating: int = cls.get_all_discounts(items).aggregate(
            Max("discount_weight")
        )["discount_weight__max"]
        priority_discount: Discounts = Discounts.objects.filter(
            discount_weight=max_rating, discount_type="d"
        ).first()
        return priority_discount

    @classmethod
    def get_cart_discount(cls, promo_code: str) -> QuerySet:
        """get and return discount by promo code"""
        discount: QuerySet = Discounts.objects.filter(promo_code=promo_code)
        return discount

    @classmethod
    def use_promo_code(cls, promo_code: str, cart: Cart) -> None:
        if cls._check_if_used_promo_code(promo_code, cart):
            discount = Discounts.objects.filter(promo_code=promo_code).first()
            if discount:
                if discount.items_qty == 0:
                    cls._apply_promo_code(discount, cart, promo_code)
                    return
                if 0 < discount.items_qty <= len(cart):
                    cls._apply_promo_code(discount, cart, promo_code)
                else:
                    cart.cart["message"] = (
                        _("Not enough goods in cart, {} is required").format(
                            discount.items_qty
                        ),
                        "danger",
                    )
            else:
                cart.cart["message"] = (_("Wrong promo code"), "danger")
        else:
            if cart.cart["promo_code_list"][0] != promo_code:
                cart.cart["message"] = (
                    _("One promo code can be used in one cart"),
                    "warning",
                )
            else:
                cart.cart["message"] = (
                    _("Promo code {} has been used already").format(promo_code),
                    "warning",
                )
        cart.save()

    @classmethod
    def _apply_promo_code(cls, discount, cart, promo_code: str):
        new_price = cart.cart["total_cart_price"]["new_price"]
        cart.cart["total_cart_price"]["old_price"] = cart.cart["total_cart_price"][
            "new_price"
        ]
        if discount.amount_type == "cashed":
            cart.cart["total_cart_price"]["new_price"] -= discount.amount
        elif discount.amount_type == "percentage":
            cart.cart["total_cart_price"]["new_price"] -= (
                new_price * discount.amount // 100
            )
        cart.cart["message"] = ()
        cart.cart["promo_code_list"].append(promo_code)
        cart.save()

    @classmethod
    def _check_if_used_promo_code(cls, promo_code: str, cart: Cart) -> bool:
        """Check if promo code was already used and return bool value"""
        if (
            promo_code in cart.cart["promo_code_list"]
            or len(cart.cart["promo_code_list"]) >= 1
        ):
            return False
        return True

    @classmethod
    def get_item_discounted_price(
        cls, item: Item, item_price: int = None, seller: Stock = None
    ):
        """
        The get_item_discounted_price function returns the discounted price of an item.
        """
        items = (
            Item.objects.filter(id=item.id)
            if not seller
            else Item.objects.filter(id=item.id, stock_item__seller=seller.seller)
        )
        priority_discount = cls.get_priority_discount(items)
        if item_price is not None:
            return cls.calculate_price_with_discount(
                item_price, discount=priority_discount
            )
        if not seller:
            max_price: int = Stock.objects.select_related("item").aggregate(
                Max("price")
            )["price__max"]
        else:
            max_price: int = (
                Stock.objects.filter(seller=seller.seller, item=item).get().price
            )
        return cls.calculate_price_with_discount(max_price, discount=priority_discount)

    @classmethod
    def calculate_price_with_discount(cls, price: int, discount: Discounts):
        if discount:
            price_with_discount = (
                price - discount.amount
                if discount.amount_type == "cashed"
                else price - (price * discount.amount // 100)
            )
            return price_with_discount
        return price
