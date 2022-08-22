from django import forms
from django.utils.translation import gettext_lazy as _


class GetAccountNumberForm(forms.Form):
    account_number = forms.CharField(
        max_length=8,
        label=_("Account number"),
        error_messages={"required": _("Field can not be empty")},
        widget=forms.TextInput(attrs={"placeholder": "9999 9999"}),
    )


class GetCardNumberForm(forms.Form):
    card_number = forms.CharField(
        max_length=16,
        label=_("Card number"),
        error_messages={"required": _("Field can not be empty")},
        widget=forms.TextInput(attrs={"placeholder": "9999 9999 9999 9999"}),
    )
