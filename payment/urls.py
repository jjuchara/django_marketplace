from django.urls import path

from .views import MakePaymentView, ProceedPaymentView

urlpatterns = [
    path(
        "get-payment-data/<str:order_number>/",
        MakePaymentView.as_view(),
        name="get_payment_data",
    ),
    path("proceed-payment/", ProceedPaymentView.as_view(), name="proceed_payment"),
]
