from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Roles(Enum):
    admin = _("admin")
    seller = _("seller")
    customer = _("customer")

    @classmethod
    def as_choices(cls):
        return (
            (cls.admin.value, "admin"),
            (cls.seller.value, "seller"),
            (cls.customer.value, "customer"),
        )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(
        max_length=8,
        choices=Roles.as_choices(),
        verbose_name=_("Role"),
        default=Roles.customer.value,
    )
    avatar = models.ImageField(
        upload_to="profiles", blank=True, verbose_name=_("avatar")
    )
    name = models.CharField(max_length=255, blank=True, verbose_name=_("Name"))
    last_name = models.CharField(
        max_length=255, blank=True, verbose_name=_("Last name")
    )
    first_name = models.CharField(
        max_length=255, blank=True, verbose_name=_("First name")
    )
    third_name = models.CharField(
        max_length=255, blank=True, verbose_name=_("Third name")
    )
    city = models.CharField(max_length=255, blank=True, verbose_name=_("City"))
    address = models.CharField(max_length=888, blank=True, verbose_name=_("Address"))
    phone_number = models.CharField(
        max_length=15, null=True, blank=True, verbose_name=_("Phone number")
    )

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
