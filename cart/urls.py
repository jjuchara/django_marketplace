from django.urls import path

from .views import CartSummary, UpdateCart, UsePromoCode

urlpatterns = [
    path("", CartSummary.as_view(), name="cart_summary"),
    path("update-cart/", UpdateCart.as_view(), name="cart_update"),
    path("use-promo-code/", UsePromoCode.as_view(), name="use_promo_code"),
]
