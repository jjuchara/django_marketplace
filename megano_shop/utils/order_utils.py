from django.utils.translation import gettext_lazy as _


def format_phone_number(number: str) -> str:
    """Return number in russian format"""
    if len(number) != 10:
        return _("Wrong number format")
    return f"+7{number[0:3]}{number[3:6]}{number[6:8]}{number[8:10]}"
