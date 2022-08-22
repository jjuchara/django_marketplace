from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("acc/", include("account.urls")),
    path("", include("megano_shop.urls")),
    path("payment/", include("payment.urls")),
    path("cart/", include("cart.urls")),
    path("i18n", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
