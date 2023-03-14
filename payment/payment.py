import json
from typing import Coroutine

from django.contrib import messages

from megano_shop.models import Order
from payment.tasks import send_payment_request


def send_payment_info_to_payment_system(
    order_number: str,
    card_number: str = None,
    account_number: str = None,
    price: int = 0,
) -> bool:
    acc_number = account_number if account_number else card_number
    data_to_sent = json.dumps(
        {"order_number": order_number, "account_number": acc_number, "price": price},
        default=str,
    )
    url = f"http://payment_api:8010/payment/{order_number}/"

    is_payed = send_payment_request.delay(data_to_sent, url)

    return is_payed.get()["payment"]["is_payed"]


def change_order_status(request, order_number: str, payment_status: Coroutine):
    order = Order.objects.get(order_number=order_number)
    if payment_status:
        messages.add_message(
            request, messages.SUCCESS, f"Оплата заказа:{order_number} прошла успешно"
        )
        order.payment_status = "p"
        order.order_status = "c"
        order.save()
    else:
        messages.add_message(
            request,
            messages.WARNING,
            f"Оплата заказа:{order_number} не успешная, пожалуйста, повторите попытку",
        )
