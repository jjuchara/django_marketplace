import json

from django.http import JsonResponse
from django.views.generic import TemplateView, View

from megano_shop.models import Item, Stock
from megano_shop.services.discounts import DiscountsService

from .cart import Cart


class CartSummary(TemplateView):
    template_name = "cart/summary.html"


class UpdateCart(View):
    @classmethod
    def post(cls, request):
        data = json.loads(request.body)
        cart_instance = Cart(request)

        action, item_id, item_qty, selected_seller = (
            data["action"],
            data["item_id"],
            data["item_qty"],
            data["selected_seller"],
        )

        item = Item.objects.get(pk=item_id)
        sellers = cart_instance.get_sellers(item)
        if item_id in cart_instance.cart["items"] and not selected_seller:
            selected_seller = cart_instance.cart["items"][item_id]["seller"]

        if not selected_seller:
            seller = cart_instance.add_random_seller(item)
        elif selected_seller:
            seller = Stock.objects.get(item=item, seller__username=selected_seller)
        if action == "add" or action == "update":
            item_price = DiscountsService.get_item_discounted_price(item, seller=seller)
        else:
            item_price = None

        cart_instance.add(
            item=item,
            item_qty=item_qty,
            seller=seller,
            sellers=sellers,
            price_with_disc=item_price,
        ) if action == "add" else cart_instance.delete(
            item=item
        ) if action == "delete" else cart_instance.update(
            item=item,
            action=action,
            seller=seller,
            item_qty=item_qty,
            price_with_disc=item_price,
        )

        item_qty = (
            cart_instance.cart["items"][item_id]["item_qty"]
            if item_id in cart_instance.cart["items"]
            else 0
        )
        cart_qty = cart_instance.__len__()
        (
            old_item_total_price,
            new_item_total_price,
        ) = cart_instance.get_items_total_price(item_id, item)
        cart_instance.get_cart_total_price()

        return JsonResponse(
            {
                "item_id": item_id,
                "action": action,
                "item_qty": item_qty,
                "cart_qty": cart_qty,
                "old_item_total_price": int(old_item_total_price),
                "new_item_total_price": int(new_item_total_price),
                "old_cart_total_price": cart_instance.cart["total_cart_price"][
                    "old_price"
                ],
                "new_cart_total_price": cart_instance.cart["total_cart_price"][
                    "new_price"
                ],
                "seller": str(seller),
                "sellers": str(sellers),
                "message": cart_instance.get_message(item_id),
            }
        )


class UsePromoCode(View):
    @classmethod
    def post(cls, request):
        data = json.loads(request.body)
        cart_instance = Cart(request)
        promo_code_text = data["promo_code"]
        DiscountsService.use_promo_code(promo_code_text, cart_instance)

        return JsonResponse(
            {
                "promoCode": promo_code_text,
                "action": data["action"],
                "old_cart_total_price": cart_instance.cart["total_cart_price"][
                    "old_price"
                ],
                "new_cart_total_price": cart_instance.cart["total_cart_price"][
                    "new_price"
                ],
                "message": cart_instance.cart["message"],
            }
        )
