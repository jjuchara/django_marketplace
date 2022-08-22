from django.http import HttpResponse


class PaymentService:
    @classmethod
    def pay_for_the_order(cls, order_id):
        """Оплата заказа"""
        return HttpResponse(f"<h1>Pay order №</h1>")

    @classmethod
    def get_order_payment_status(cls, order_id):
        """Получить статус оплаты заказа"""
        return HttpResponse(f"<h1>Order payment status</h1>")
