from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _

from megano_shop.utils.filter_utils import (
    availability_choices,
    manufacturers_list,
    sellers_list,
)

from .models import Reviews
from .utils.order_utils import format_phone_number


class ReviewsForm(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = ("content", "user", "item")

    def __init__(self, *args, **kwargs):
        super(ReviewsForm, self).__init__(*args, **kwargs)
        self.fields["content"].widget.attrs["class"] = "form-textarea"
        self.fields["content"].widget.attrs["name"] = "review"
        self.fields["content"].widget.attrs["id"] = "review"
        self.fields["content"].widget.attrs["placeholder"] = "Review"


class ItemsFilterForm(forms.Form):
    SORTING_CHOICE = (
        ("cheap_first", _("Cheap first")),
        ("expensive_first", _("Expensive first")),
        ("popular_first", _("Popular first")),
        ("not_popular_first", _("Not popular first")),
        ("new_first", _("New first")),
        ("old_first", _("Old first")),
    )

    price_min = forms.DecimalField(label=_("price min"), required=False)
    price_max = forms.DecimalField(label=_("price max"), required=False)
    title = forms.CharField(max_length=255, label=_("title"), required=False)
    seller = forms.MultipleChoiceField(
        choices=sellers_list(),
        widget=forms.CheckboxSelectMultiple,
        label=_("seller"),
        required=False,
    )
    manufacturer = forms.MultipleChoiceField(
        choices=manufacturers_list(),
        initial="",
        widget=forms.SelectMultiple(),
        required=False,
        label=_("manufacturer"),
    )
    available = forms.ChoiceField(
        required=False,
        label=_("available"),
        widget=forms.RadioSelect,
        choices=availability_choices,
    )
    sorting_order = forms.ChoiceField(
        required=False, choices=SORTING_CHOICE, label=_("Sort by")
    )


class OrderUserInfoForm(forms.Form):
    full_name = forms.CharField(
        max_length=255,
        required=False,
        label=_("User name"),
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "id": "name",
                "type": "text",
                "placeholder": "Иванов Иван Иванович",
            }
        ),
    )
    phone_number = forms.CharField(
        max_length=12,
        required=False,
        label=_("Phone number"),
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "id": "phone",
                "type": "text",
                "placeholder": format_phone_number("9187456654"),
            }
        ),
    )

    email = forms.CharField(
        max_length=60,
        error_messages={"required": _("Field can't be blank")},
        validators=[EmailValidator(message=_("Enter correct -mail address"))],
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "id": "mail",
                "type": "text",
                "value": "",
                "label": "E-mail",
            }
        ),
    )
    password1 = forms.CharField(
        max_length=255,
        required=False,
        error_messages={"required": _("Field can't be blank")},
        validators=[validate_password],
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "id": "password1",
                "name": "password",
                "type": "password",
                "placeholder": _("Password can be changed here"),
            }
        ),
    )
    password2 = forms.CharField(
        max_length=255,
        required=False,
        error_messages={"required": _("Field can't be blank")},
        validators=[validate_password],
        label=_("Password confirmation"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "id": "password2",
                "name": "password",
                "type": "password",
                "label": "Пароль",
                "placeholder": _("Password can be changed here"),
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(OrderUserInfoForm, self).__init__(*args, **kwargs)

    def clean_full_name(self):
        data = self.cleaned_data["full_name"]
        self.validate_not_empty(data)
        if len(data.split()) != 3:
            self.add_error(
                "full_name", forms.ValidationError(_("Please enter your complete name"))
            )
        return data

    def clean_phone_number(self):
        data = self.cleaned_data["phone_number"]
        self.validate_not_empty(data)
        if data[0:2] != "+7" or 11 > len(data[2:]) < 10:
            raise forms.ValidationError(
                _("Wrong phone number format -> {}".format(data))
            )
        return data

    def clean_password1(self):
        password1 = self.cleaned_data["password1"]
        if not self.request.user.is_authenticated and not password1:
            raise forms.ValidationError(_("Field can't be blank"))
        return password1

    def clean_password2(self):
        if not self.request.user.is_authenticated:
            password1 = self.cleaned_data.get("password1")
            password2 = self.cleaned_data["password2"]
            if not password2:
                raise forms.ValidationError(_("Field can't be blank"))
            if password1 != password2:
                raise forms.ValidationError(_("Passwords must be equal"))
            return password2

    @classmethod
    def validate_not_empty(cls, field_data: str):
        if not field_data:
            raise forms.ValidationError(_("Field can't be blank"))


class OrderDeliveryInfoForm(forms.Form):
    DELIVERY_CHOICE = (
        ("ordinary", _("Ordinary delivery")),
        ("express", _("Express delivery")),
    )
    delivery_type = forms.CharField(
        widget=forms.RadioSelect(choices=DELIVERY_CHOICE),
        initial="ordinary",
        label=_("Delivery"),
    )
    city = forms.CharField(
        max_length=250,
        label=_("City"),
        error_messages={"required": _("Field can't be blank")},
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    address = forms.CharField(
        label=_("Address"),
        error_messages={"required": _("Field can't be blank")},
        widget=forms.Textarea(attrs={"class": "form-textarea"}),
    )


class OrderPaymentTypeForm(forms.Form):
    PAYMENT_CHOICE = (
        ("online_card", _("Online")),
        ("online_account", _("Online from random person's account")),
    )
    payment_type = forms.CharField(
        widget=forms.RadioSelect(choices=PAYMENT_CHOICE),
        initial="online_card",
        label=_("Payment method"),
    )
