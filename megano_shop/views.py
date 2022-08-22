import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Count, Min
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
)
from random_username.generate import generate_username

from account.models import Profile
from cart.cart import Cart

from .forms import (
    ItemsFilterForm,
    OrderDeliveryInfoForm,
    OrderPaymentTypeForm,
    OrderUserInfoForm,
    ReviewsForm,
)
from .models import Banner, Category, Discounts, Item, Order, OrderCart, Reviews, Stock
from .services.compare import Compare, add_message_to_front
from .services.goods_views import GoodsViewsService
from .services.reviews import ReviewsService
from .utils.cache_utils import add_to_cache
from .utils.filter_utils import form_cleaned_data_filters, form_cleaned_data_sorting
from .utils.order_utils import format_phone_number


def index_page(request):
    banners = Banner.objects.filter(is_active=True)
    limited_offer = Item.objects.order_by("?").first()
    current_datetime = timezone.now() + timedelta(5)
    current_datetime = current_datetime.strftime("%d.%m.%Y %H:%M:%S")
    top_items = Item.objects.filter(status="a").order_by("-count_view")[:8]
    return render(
        request,
        "index.html",
        {
            "banners": banners,
            "top_items": top_items,
            "limited_offer": limited_offer,
            "current_datetime": current_datetime,
        },
    )


class CompareListView(TemplateView):
    template_name = "megano_shop/compare.html"
    context_object_name = "compare_list"

    @classmethod
    def post(cls, request):
        data = json.loads(request.body)
        return JsonResponse({"foo": "bar"})


class AddToCompareList(View):
    def post(self, request):
        data = json.loads(request.body)
        status = Compare.add_item_to_compare(
            item_slug=data["item_slug"],
            compare_session_key="compare_items",
            session_obj=self.request.session,
        )
        django_messages = add_message_to_front(
            data=data, status=status, request=request
        )

        compare_item_quantity = Compare.get_compare_items_quantity(
            compare_session_key="compare_items", session_obj=self.request.session
        )

        return JsonResponse(
            {
                "compare_item_quantity": compare_item_quantity,
                "messages": django_messages,
            }
        )


def delete_from_compare_list(request, slug, **kwargs):
    Compare.delete_item_from_compare(
        item_slug=slug, compare_session_key="compare_items", session_obj=request.session
    )
    messages.success(request, f"Товар {slug} удален из списка сравнения")
    return redirect("compare_list")


class OrderUserInfoView(FormView):
    form_class = OrderUserInfoForm
    template_name = "megano_shop/get_user_info.html"
    success_url = "get_delivery_info"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "GET":
            if self.request.user.is_authenticated:
                current_user = self.request.user
                user_profile = Profile.objects.get(user=current_user)
                full_name = f"{user_profile.last_name} {user_profile.first_name} {user_profile.third_name}"
                form = OrderUserInfoForm(
                    initial={
                        "full_name": full_name,
                        "phone_number": format_phone_number(user_profile.phone_number),
                        "email": current_user.email,
                    }
                )
                context["form"] = form
            else:
                form = OrderUserInfoForm()
                context["form"] = form

        return context

    def form_valid(self, form):
        cart = Cart(self.request)
        last_name, first_name, third_name = form.cleaned_data["full_name"].split()
        phone_number = form.cleaned_data["phone_number"][2:]
        email = form.cleaned_data["email"]
        password1 = form.cleaned_data["password1"]
        password2 = form.cleaned_data["password2"]
        user_exist = User.objects.filter(email=email)
        if self.request.user not in user_exist:
            try:
                if not user_exist:
                    user = self.register_and_login_user(
                        self.request,
                        first_name=first_name,
                        third_name=third_name,
                        last_name=last_name,
                        phone_number=phone_number,
                        email=email,
                        password1=password1,
                    )
                    self.create_order(user, cart)
                else:
                    form.add_error(None, "Такой пользователь уже существует")
                    raise ValidationError("Такой пользователь уже существует")

            except ValidationError:
                return super().form_invalid(form)

        else:
            self.create_order(user=self.request.user, cart=cart)

        return super().form_valid(form)

    @classmethod
    def register_and_login_user(
        cls, request, first_name, third_name, last_name, phone_number, email, password1
    ):
        username = generate_username(1)[0]
        user = User.objects.create_user(
            username=username, email=email, password=make_password(password1)
        )
        Profile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            third_name=third_name,
            phone_number=phone_number,
        )
        authenticate(username=username, password=password1)
        login(request, user)
        return user

    @classmethod
    def create_order(cls, user, cart):
        if not Order.objects.filter(buyer=user, order_status="o").exists():
            order = Order.objects.create(order_number=get_random_string(6), buyer=user)
        else:
            order = Order.objects.get(buyer=user)
        cart.add_cart_to_order(order)


class OrderDeliveryInfoView(FormView):
    form_class = OrderDeliveryInfoForm
    template_name = "megano_shop/get_delivery_info.html"
    success_url = "get_payment_type_info"

    def get_context_data(self, **kwargs):
        context = super(OrderDeliveryInfoView, self).get_context_data(**kwargs)
        user = self.request.user
        if self.request.method == "GET":
            if user.is_authenticated and user.profile.city and user.profile.address:
                form = OrderDeliveryInfoForm(
                    initial={"city": user.profile.city, "address": user.profile.address}
                )
            else:
                form = OrderDeliveryInfoForm()
            context["form"] = form
        return context

    def form_valid(self, form):
        delivery_type = form.cleaned_data["delivery_type"]
        city = form.cleaned_data["city"]
        address = form.cleaned_data["address"]
        user = self.request.user

        order = Order.objects.filter(order_status="o").get(buyer=user)
        order.shipping_type = delivery_type
        order.save()

        if user.profile.city == city and user.profile.address == address:
            pass
        else:
            user.profile.city = city
            user.profile.address = address
            user.profile.save()

        return super(OrderDeliveryInfoView, self).form_valid(form)


class OrderPaymentTypeView(FormView):
    form_class = OrderPaymentTypeForm
    template_name = "megano_shop/get_payment_type_info.html"
    success_url = "submit_order"

    def form_valid(self, form):
        payment_type = form.cleaned_data["payment_type"]
        user = self.request.user
        order = Order.objects.filter(order_status="o").get(buyer=user)
        order.payment_method = payment_type
        order.save()
        return super(OrderPaymentTypeView, self).form_valid(form)


class OrderSubmitView(ListView):
    model = Order
    template_name = "megano_shop/submit_order.html"
    context_object_name = "orders"

    def get_queryset(self):
        queryset = Order.objects.filter(buyer=self.request.user, order_status="o")
        return queryset


class ItemListView(ListView):
    paginate_by = 3
    model = Item
    template_name = "megano_shop/catalog.html"
    context_object_name = "items"

    def get(self, request, **kwargs):
        category_title = self.kwargs["instance"]
        form = ItemsFilterForm(request.GET)
        category = Category.objects.get(title=category_title)
        items = cache.get(f"{category_title}_items")
        if not items:
            if category.is_leaf_node():
                items = Item.objects.filter(category=category, status="a")
            else:
                items = Item.objects.filter(category__parent_id=category.id, status="a")
            add_to_cache(items, f"{category_title}_items")
        if form.is_valid():
            filters = form_cleaned_data_filters(form.cleaned_data)
            items = items.filter(**filters).distinct().order_by("title")
            if form.cleaned_data["sorting_order"]:
                items = form_cleaned_data_sorting(form.cleaned_data, items)
            paginator = Paginator(items, 3)
            page_number = request.GET.get("page", 1)
            page_obj = paginator.get_page(page_number)

            """We check all products in the discount, make a list of id and display only products with these ids"""
            if request.GET.get("sale_id"):
                discount = Discounts.objects.filter(id=request.GET.get("sale_id"))
                discount_products_id = []
                for elem in discount:
                    for product in elem.item.all():
                        discount_products_id.append(product.id)
                    items = Item.objects.filter(id__in=discount_products_id)
                    paginator = Paginator(items, 20)
                    page_number = request.GET.get("page", 1)
                    page_obj = paginator.get_page(page_number)
                # return render(request, 'megano_shop/catalog.html', context={'form': form, 'page_obj': page_obj})
            return render(
                request,
                "megano_shop/catalog.html",
                context={"form": form, "page_obj": page_obj},
            )
        return render(request, "megano_shop/catalog.html", context={"form": form})


class ReviewsListView(View):
    model = Reviews

    def get(self, request, goods_id):
        return ReviewsService.get_reviews_list(goods_id)


class ReviewAddView(CreateView):
    model = Reviews

    def get(self, request, goods_id):
        return ReviewsService.post_review(goods_id)


def viewed_goods(request, user_id):
    return GoodsViewsService.get_viewed_list(user_id)


def add_to_viewed(request, user_id, goods_id):
    return GoodsViewsService.add_to_viewed(user_id, goods_id)


def viewed_goods_number(request, user_id):
    return GoodsViewsService.get_viewed_number(user_id)


def delete_from_viewed(request, user_id, goods_id):
    return GoodsViewsService.delete_from_viewed(user_id, goods_id)


def is_viewed(request, user_id, goods_id):
    return GoodsViewsService.is_viewed(user_id, goods_id)


class ProductDetailView(DetailView):
    """Product detail view"""

    model = Item
    template_name = "product.html"
    context_object_name = "item"
    queryset = Item.objects.all().prefetch_related("category")

    def get_success_url(self):
        return reverse("product_detail", kwargs={"id": self.object.id})

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        current_item = Item.objects.get(id=pk)
        specifications_list = [
            {key: value} for key, value in current_item.specifications.items()
        ]
        stocks = Stock.objects.select_related("seller").filter(item=current_item.id)
        stocks = stocks.order_by("price")
        reviews = ReviewsService.get_reviews_list(current_item.id, request)
        reviews_count = ReviewsService.get_count_reviews(current_item.id)
        reviews_form = ReviewsForm(
            initial={"user": self.request.user.id, "item": current_item}
        )
        return render(
            request,
            "product.html",
            {
                "reviews_form": reviews_form,
                "reviews": reviews,
                "reviews_count": reviews_count,
                "current_item": current_item,
                "stocks": stocks,
                "specifications_list": specifications_list,
            },
        )

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        current_item = Item.objects.get(id=pk)
        ReviewsService.post_review(current_item.id, request)
        return redirect("product_detail", pk)


def sales_list(request):
    discount_list = Discounts.objects.filter(discount_type="d", is_active=True)
    p = Paginator(discount_list, 20)
    page_number = request.GET.get("page")
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    return render(
        request,
        "megano_shop/sale.html",
        {"discount_list": discount_list, "page_obj": page_obj},
    )


def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    goods = OrderCart.objects.filter(order=order_id)
    return render(
        request, "oneorder.html", {"order": order, "order_id": order_id, "goods": goods}
    )


def seller_detail(request, seller_username):
    seller = User.objects.get(username=seller_username)
    context = {"seller": seller}
    return render(request, "account/account.html", context)
