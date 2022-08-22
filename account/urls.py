from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    AccountView,
    editing_profile,
    login_view,
    orders_history,
    registration_view,
    reset_password_1,
    reset_password_2,
    views_history,
)

urlpatterns = [
    path("registration/", registration_view, name="reg"),
    path("account/<str:username>/", AccountView.as_view(), name="account"),
    path("account/<str:username>/orders", orders_history, name="orders"),
    path("account/<str:username>/watchlist", views_history, name="views"),
    path(
        "account/edit_profile/<str:username>/", editing_profile, name="editing_profile"
    ),
    path("password-reset/", reset_password_1, name="password-reset-1"),
    path(
        "password-reset/confirm/<uidb64>/<token>",
        reset_password_2,
        name="password-reset-2",
    ),
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
