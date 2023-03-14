import mptt_urls
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path

from .models import Category
from .views import (
    AddToCompareList,
    CompareListView,
    ItemListView,
    OrderDeliveryInfoView,
    OrderPaymentTypeView,
    OrderSubmitView,
    OrderUserInfoView,
    ProductDetailView,
    ReviewAddView,
    ReviewsListView,
    add_to_viewed,
    delete_from_compare_list,
    delete_from_viewed,
    index_page,
    is_viewed,
    order_detail,
    sales_list,
    seller_detail,
    viewed_goods,
    viewed_goods_number,
)

urlpatterns = [
    path("", index_page, name="index"),
    re_path(
        r"category/(?P<path>.*)",
        mptt_urls.view(model=Category, view=ItemListView.as_view()),
        name="filtered_category",
    ),
    path("compare/", CompareListView.as_view(), name="compare_list"),
    path("add_to_compare/", AddToCompareList.as_view(), name="add_to_compare"),
    path(
        "delete_from_compare/<slug:slug>",
        delete_from_compare_list,
        name="delete_from_compare_list",
    ),
    path("cart/get_user_info", OrderUserInfoView.as_view(), name="get_user_info"),
    path(
        "cart/get_delivery_info",
        OrderDeliveryInfoView.as_view(),
        name="get_delivery_info",
    ),
    path(
        "cart/get_payment_type_info",
        OrderPaymentTypeView.as_view(),
        name="get_payment_type",
    ),
    path("cart/submit_order", OrderSubmitView.as_view(), name="submit_order"),
    path("sales/", sales_list, name="sales_list"),
    path("order/<str:order_id>", order_detail, name="order_detail"),
    path(
        "catalog/<int:goods_id>/reviews/",
        ReviewsListView.as_view(),
        name="reviews_list",
    ),
    path(
        "catalog/<int:goods_id>/add_review/", ReviewAddView.as_view(), name="review_add"
    ),
    path("catalog/<int:pk>/detail", ProductDetailView.as_view(), name="product_detail"),
    path("catalog/<int:user_id>/views/", viewed_goods, name="viewed_goods"),
    path(
        "catalog/<int:user_id>-<int:goods_id>/add_to_viewed/",
        add_to_viewed,
        name="add_to_viewed",
    ),
    path(
        "catalog/<int:user_id>/viewed_number/",
        viewed_goods_number,
        name="viewed_goods_number",
    ),
    path(
        "catalog/<int:user_id>-<int:goods_id>/delete_from_viewed/",
        delete_from_viewed,
        name="delete_from_viewed",
    ),
    path(
        "catalog/<int:user_id>-<int:goods_id>/is_viewed/", is_viewed, name="is_viewed"
    ),
    path("seller/<str:seller_username>/", seller_detail, name="seller"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
