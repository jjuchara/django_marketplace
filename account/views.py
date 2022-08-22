import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import ListView

from megano_shop.models import Item, Order, Views

from .forms import (
    AuthForm,
    EditingForm,
    RegistrationForm,
    ResetPasswordForm_1,
    ResetPasswordForm_2,
)
from .models import Profile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def registration_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            name = form.cleaned_data.get("name")

            username = email.split("@")[0]
            first_name, last_name = name.strip().split()

            user = User.objects.create(
                username=username,
                password=make_password(password),
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            Profile.objects.create(user=user, phone_number="9999999999")

            user = authenticate(username=user.username, password=password)
            if user:
                login(request, user)

                return redirect("/")
            else:
                form.add_error("__all__", "Account not found")

            return redirect("/")

    else:
        form = RegistrationForm()

    return render(request, "registr.html", {"form": form})


class AccountView(ListView):
    model = Profile
    template_name = "account/account.html"

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        context["orders"] = Order.objects.filter(buyer=self.request.user.id)
        view_list = Views.objects.filter(user=self.request.user.id)
        context["views"] = Item.objects.filter(id__in=view_list).prefetch_related(
            "discount"
        )
        return context


# +
def editing_profile(request, username):
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    if request.method == "POST":
        profile_form = EditingForm(request.POST, request.FILES)

        if profile_form.is_valid():
            avatar = profile_form.cleaned_data.get("avatar")
            name = profile_form.cleaned_data.get("name")
            phone_number = profile_form.cleaned_data.get("phone_number")
            email = profile_form.cleaned_data.get("email")
            password1 = profile_form.cleaned_data.get("password1")
            password2 = profile_form.cleaned_data.get("password2")

            logger.info(f"avatar - {avatar}")

            if avatar != None:
                request.user.profile.avatar = avatar
            if name != "":
                first_name, last_name = name.strip().split()
                request.user.first_name = first_name
                request.user.last_name = last_name
            if phone_number != "":
                request.user.profile.phone_number = phone_number[2:]
            if email != "":
                request.user.email = email

            if password1 != "" and password1 == password2:
                request.user.set_password(password1)

            request.user.save()
            request.user.profile.save()
            success_msg = "Профиль успешно сохранен!"

            user = authenticate(username=user.username, password=password1)
            if user:
                login(request, user)

            return render(
                request,
                "account/profile.html",
                {
                    "profile": profile,
                    "profile_form": profile_form,
                    "success_msg": success_msg,
                },
            )

    else:
        profile_form = EditingForm(
            initial={
                "name": user.first_name + " " + user.last_name,
                "phone_number": "+7" + profile.phone_number,
                "email": user.email,
            }
        )

    return render(
        request,
        "account/profile.html",
        {"profile": profile, "profile_form": profile_form},
    )


def reset_password_1(request):
    if request.method == "POST":
        form = ResetPasswordForm_1(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")

            user = User.objects.get(email=email)

            uidb = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            context = {
                "first_name": user.profile.first_name,
                "last_name": user.profile.last_name,
                "uidb": uidb,
                "token": token,
            }
            message_mail = render_to_string("message_to_the_mail.html", context)
            em = EmailMultiAlternatives(
                subject="New password", body="Password change", to=[email]
            )
            em.attach_alternative(message_mail, "text/html")

            em.send()
            # return HttpResponse("Сообщение отправлено")
            messages.add_message(request, messages.INFO, "The message has been sent")

    else:
        form = ResetPasswordForm_1()

    return render(request, "e-mail.html", {"form": form})


def reset_password_2(request, uidb64, token):
    if request.method == "POST":
        form = ResetPasswordForm_2(request.POST)
        if form.is_valid():
            new_pas = form.cleaned_data.get("new_password")

            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(id=uid)
            user.set_password(new_pas)
            user.save()
            return redirect("/")

    else:
        form = ResetPasswordForm_2()

    return render(request, "password.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = User.objects.get(email=email)

            user = authenticate(username=user.username, password=password)

            if user:
                login(request, user)
                return redirect("/")
            else:
                form.add_error("__all__", "Account not found")

    else:
        form = AuthForm()

    return render(request, "login.html", {"form": form})


def orders_history(request, username):
    orders = Order.objects.filter(buyer=request.user.id)
    return render(
        request, "historyorder.html", {"orders": orders, "username": username}
    )


def views_history(request, username):
    view_list = Views.objects.filter(user=request.user.id)
    views = Item.objects.filter(id__in=view_list).prefetch_related("discount")
    return render(request, "historyview.html", {"views": views, "username": username})
