import time

from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from megano_shop.models import Order

from .forms import GetAccountNumberForm, GetCardNumberForm
from .payment import change_order_status, send_payment_info_to_payment_system


class MakePaymentView(FormView):
    form_class = GetAccountNumberForm
    template_name = "payment/payment-data.html"

    def get_success_url(self):
        return reverse("proceed_payment")

    def get_form_class(self):
        order_number = self.request.path.split("/")[3]
        order = Order.objects.get(order_number=order_number)
        if order.payment_method == "online_card":
            return GetCardNumberForm
        elif order.payment_method == "online_account":
            return GetAccountNumberForm

    def get_form(self, form_class=None):
        form = super(MakePaymentView, self).get_form()
        return form

    def get_context_data(self, **kwargs):
        form = self.get_form()
        context = super(MakePaymentView, self).get_context_data(**kwargs)
        context["form"] = form
        context["form_class"] = form.__class__.__name__
        return context

    def form_valid(self, form):
        order_number = self.request.path.split("/")[3]
        self.request.session["order_number"] = order_number
        if self.get_form_class() == GetCardNumberForm:
            card_number = form.cleaned_data["card_number"]
            self.request.session["acc_number"] = card_number
        else:
            account_number = form.cleaned_data["account_number"]
            self.request.session["acc_number"] = account_number
        return redirect(reverse("proceed_payment"))


class ProceedPaymentView(TemplateView):
    # template_name = 'payment/progressPayment.html'

    def get(self, request, *args, **kwargs):
        order_number = request.session.get("order_number", None)
        acc_number = request.session.get("acc_number", None)
        payment_amount = Order.objects.get(
            order_number=order_number
        ).calculate_price_with_ship

        time.sleep(5)
        payment_status = send_payment_info_to_payment_system(
            order_number=order_number, card_number=acc_number, price=payment_amount
        )
        change_order_status(request, order_number, payment_status)

        return redirect(reverse("orders", kwargs={"username": request.user}))
