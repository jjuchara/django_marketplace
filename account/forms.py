import re

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class RegistrationForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": _("name")}), label=""
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"placeholder": "email"}), label=""
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": _("password")}), label=""
    )

    def clean_name(self):
        name = self.cleaned_data.get("name")
        full_name = re.findall(r"\w+", name)
        if len(full_name) != 2:
            raise ValidationError("First name and last name (Ivan Ivanov)")
        return name

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("This email is already registered"))
        return email


class EditingForm(forms.Form):
    avatar = forms.FileField(required=False)
    name = forms.CharField(max_length=255, required=False, label="FIO")
    phone_number = forms.CharField(max_length=40, required=False)
    email = forms.EmailField(required=False)

    password1 = forms.CharField(widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(EditingForm, self).__init__(*args, **kwargs)
        self.fields["avatar"].widget.attrs["class"] = "Profile-file form-input"
        self.fields["avatar"].widget.attrs["id"] = "avatar"
        self.fields["avatar"].widget.attrs["name"] = "avatar"
        self.fields["avatar"].widget.attrs["type"] = "file"
        self.fields["avatar"].widget.attrs["data-validate"] = "onlyImgAvatar"

        self.fields["phone_number"].widget.attrs["class"] = "form-input"
        self.fields["phone_number"].widget.attrs["id"] = "phone"
        self.fields["phone_number"].widget.attrs["name"] = "phone"
        self.fields["phone_number"].widget.attrs["type"] = "text"
        self.fields["phone_number"].widget.attrs["data-validate"] = "require"

        self.fields["email"].widget.attrs["class"] = "form-input"
        self.fields["email"].widget.attrs["id"] = "phone"
        self.fields["email"].widget.attrs["name"] = "phone"
        self.fields["email"].widget.attrs["type"] = "text"
        self.fields["email"].widget.attrs["data-validate"] = "require"

        self.fields["name"].widget.attrs["class"] = "form-input"
        self.fields["name"].widget.attrs["id"] = "name"
        self.fields["name"].widget.attrs["name"] = "name"
        self.fields["name"].widget.attrs["type"] = "text"
        self.fields["name"].widget.attrs["data-validate"] = "require"

        self.fields["password1"].widget.attrs["class"] = "form-input"
        self.fields["password1"].widget.attrs["id"] = "password"
        self.fields["password1"].widget.attrs["name"] = "password"
        self.fields["password1"].widget.attrs["type"] = "password"
        self.fields["password1"].widget.attrs[
            "placeholder"
        ] = "Тут можно изменить пароль"

        self.fields["password2"].widget.attrs["class"] = "form-input"
        self.fields["password2"].widget.attrs["id"] = "passwordReply"
        self.fields["password2"].widget.attrs["name"] = "passwordReply"
        self.fields["password2"].widget.attrs["type"] = "password"
        self.fields["password2"].widget.attrs["placeholder"] = "Введите пароль повторно"

    def clean(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 != password2:
            msg = "Пароли должны совпадать"
            self.add_error("password1", msg)
            self.add_error("password2", msg)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        emails = User.objects.filter(email=email)
        if len(emails) > 1:
            raise ValidationError("This email is already registered")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        pattern = re.compile("^((\+7)+([0-9]){10})$")
        if not pattern.match(phone_number):
            self.add_error(
                "phone_number", "Введите номер телефона в формате +71234567890"
            )
        return phone_number


class ResetPasswordForm_1(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"placeholder": "E-mail"}), label=""
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Such email is not registered")
        return email


class ResetPasswordForm_2(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "password"}), label=""
    )


class AuthForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"placeholder": "E-mail"}), label=""
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "*********"}), label=""
    )
