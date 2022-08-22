import random
from dataclasses import asdict, dataclass, field
from decimal import Decimal

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from megano_shop.models import Item, OrderCart, Stock


@dataclass
class CartData:
    title: str
    subtitle: str
    img: str
    seller: str
    sellers: list = field(default_factory=list)
    item_qty: int = 1
    item_price: dict[str, int] = field(default_factory=dict)
    total_item_price: dict[str, int] = field(default_factory=dict)
    message: tuple = field(default_factory=tuple)


class Cart:
    """
    A base Cart class, providing some default behaviors that
    can be inherited or overrided, as necessary.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if settings.CART_SESSION_ID not in request.session:
            cart = self.session[settings.CART_SESSION_ID] = {
                "items": {},
                "total_cart_price": {"old_price": 0, "new_price": 0},
                "message": (),
                "promo_code_list": [],
            }
        self.cart = cart

    def add(self, item, item_qty, seller, sellers, price_with_disc: int):
        """Add item to cart session"""
        item_id = str(item.id)

        if item_id in self.cart["items"]:
            if self._check_stock_balance(seller, item_id, item_qty):
                self.cart["items"][item_id]["item_qty"] += int(item_qty)
                self.cart["items"][item_id]["message"] = (
                    _("Item {} is added to cart").format(item),
                    "success",
                )
            else:
                self.cart["items"][item_id]["message"] = (
                    _("Not enough goods in stock!"),
                    "danger",
                )
            # self._apply_discount(item, item_id)
        else:
            cart_data = CartData(
                title=item.title,
                subtitle=item.description,
                img=item.main_image.url,
                seller=str(seller),
                sellers=sellers,
                item_qty=int(item_qty),
                item_price={"old_price": 0, "new_price": int(price_with_disc)},
                total_item_price={"old_price": 0, "new_price": int(price_with_disc)},
            )
            if not self._check_stock_balance(
                item_id=item_id, stock=seller, item_qty=item_qty
            ):
                cart_data.item_qty = seller.quantity
                cart_data.message = (_("Not enough goods in stock!"), "danger")
            else:
                cart_data.message = (
                    _("Item {} is added to cart").format(item),
                    "success",
                )
            self.cart["items"][item_id] = asdict(cart_data)
            self.cart["message"] = ()
        self.save()

    def delete(self, item):
        """Delete item from cart session"""
        item_id = str(item.id)
        if item_id in self.cart["items"]:
            del self.cart["items"][item_id]
            self.save()

    def update(self, item, action: str, seller, item_qty: int, price_with_disc: int):
        """
        Increase or decrease item quantity in cart
        """
        item_id = str(item.id)
        if item_id in self.cart["items"]:
            if action == "increase":
                if self._check_stock_balance(
                    stock=seller, item_id=item_id, item_qty=item_qty
                ):
                    self.cart["items"][item_id]["item_qty"] += 1
                else:
                    self.cart["items"][item_id]["message"] = (
                        _("Not enough goods in stock!"),
                        "danger",
                    )
            elif action == "decrease":
                self.cart["items"][item_id]["message"] = ()
                if self.cart["items"][item_id]["item_qty"] <= 1:
                    self.delete(item)
                else:
                    self.cart["items"][item_id]["item_qty"] -= 1
            elif action == "update":
                self.change_seller(item_id, seller, item_qty, price_with_disc)
            self.cart["promo_code_list"] = []
            self.save()

    def __len__(self):
        """
        Get cart data and sum cart items
        """
        if not self.cart["items"]:
            return 0
        return sum(item["item_qty"] for item in self.cart["items"].values())

    def get_items_total_price(self, item_id, item) -> tuple[int, int]:
        """
        Get cart data and sum total price for product and old prise, if is discount
        """
        old_price: int = 0
        new_price: int = 0
        if item_id in self.cart["items"]:
            new_price = (
                self.cart["items"][item_id]["item_price"]["new_price"]
                * self.cart["items"][item_id]["item_qty"]
            )
            old_price = (
                self.cart["items"][item_id]["item_price"]["old_price"]
                * self.cart["items"][item_id]["item_qty"]
            )
            self.cart["items"][item_id]["total_item_price"]["new_price"] = new_price
            self.cart["items"][item_id]["total_item_price"]["old_price"] = old_price

            return old_price, new_price
        return old_price, new_price

    def get_cart_total_price(self):
        """
        Get cart data and calculate total price for all cart and total price for cart with old price
        """
        if self.__len__() < 1:
            self.cart["total_cart_price"]["old_price"] = 0
            self.cart["total_cart_price"]["new_price"] = 0
        new_price = sum(
            Decimal(item["item_price"]["new_price"]) * item["item_qty"]
            for item in self.cart["items"].values()
        )
        old_price = sum(
            Decimal(item["item_price"]["old_price"]) * item["item_qty"]
            for item in self.cart["items"].values()
        )

        self.cart["total_cart_price"] = {
            "old_price": int(old_price),
            "new_price": int(new_price),
        }
        self.save()

    def save(self):
        self.session.modified = True

    def delete_cart(self):
        del self.session[settings.CART_SESSION_ID]

    @classmethod
    def add_random_seller(cls, item):
        sellers = item.stock_item.filter(quantity__gte=1)
        return random.choice(sellers)

    @classmethod
    def get_sellers(cls, item):
        sellers = item.stock_item.filter(quantity__gte=1)
        sellers_list = [seller.seller.username for seller in sellers]
        return sellers_list

    def change_seller(self, item_id: str, seller, item_qty, price_with_disc: int):
        self.cart["items"][item_id]["seller"] = str(seller.seller)
        self.cart["items"][item_id]["item_price"]["new_price"] = int(price_with_disc)
        if not self._check_stock_balance(seller, item_id, item_qty):
            self.cart["items"][item_id]["item_qty"] = seller.quantity
            self.cart["items"][item_id]["message"] = (
                _("Not enough goods in stock, available qty is {}").format(
                    seller.quantity
                ),
                "danger",
            )

    def _check_stock_balance(self, stock, item_id: str, item_qty: int) -> bool:
        if item_id in self.cart["items"]:
            if stock.quantity > self.cart["items"][item_id]["item_qty"]:
                return True
            return False
        else:
            if stock.quantity >= int(item_qty):
                return True
            return False

    def get_message(self, item_id) -> str:
        if item_id in self.cart["items"]:
            message = self.cart["items"][item_id]["message"]
            self.cart["items"][item_id]["message"] = ""
            return message
        else:
            return ""

    def add_cart_to_order(self, order):
        cart = self.cart
        for key, value in cart["items"].items():
            item = Item.objects.get(id=key)
            stock = Stock.objects.filter(seller__username=value["seller"]).get(
                item=item
            )
            cart_item = OrderCart.objects.filter(order=order, item=item, stock=stock)
            if cart_item:
                cart_item = cart_item.first()
                if stock.quantity >= cart_item.items_qty + value["item_qty"]:
                    cart_item.items_qty += value["item_qty"]
                    cart_item.total_price += Decimal(
                        value["total_item_price"]["new_price"]
                    )
                    cart_item.save()
                    self._update_stock_items_amount(cart_item)
                else:
                    cart_item.items_qty += stock.quantity
                    cart_item.total_price += Decimal(stock.quantity * stock.price)
                    cart_item.save()
                    self._update_stock_items_amount(cart_item)
            else:
                cart_item = OrderCart.objects.create(
                    order=order,
                    item=item,
                    stock=stock,
                    items_price=Decimal(value["item_price"]["new_price"]),
                    items_qty=value["item_qty"],
                    total_price=value["total_item_price"]["new_price"],
                )

                self._update_stock_items_amount(cart_item=cart_item)
        self._update_total_order_price(order=order)
        self.delete_cart()

    @classmethod
    def _update_stock_items_amount(cls, cart_item):
        stock = cart_item.stock
        if stock.quantity > 0:
            stock.quantity -= cart_item.items_qty
            if stock.quantity < 0:
                stock.quantity = 0
                stock.save()
            stock.save()
        cls._update_item_active_flug(cart_item)

    @classmethod
    def _update_item_active_flug(cls, cart_item):
        item = cart_item.item
        total_item_qty = 0
        for i in item.stock_item.all():
            total_item_qty += i.quantity
        cart_item.item.status = (
            "i" if not cls._check_if_items_exists(total_item_qty) else "a"
        )
        cart_item.item.save()

    @classmethod
    def _check_if_items_exists(cls, item):
        return False if item == 0 else True

    def _update_total_order_price(self, order):
        if order.total_price == 0:
            total_order_price = self.cart["total_cart_price"]["new_price"]
        else:
            total_order_price = (
                order.total_price + self.cart["total_cart_price"]["new_price"]
            )

        order.total_price = total_order_price
        order.save()
