from typing import Iterable

from django.contrib import messages
from django.contrib.sessions.backends.base import SessionBase
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _


class Compare:
    """Service for add, delete, get_quantity, get_list compare items"""

    @classmethod
    def _check_if_session_dict_exist(
        cls, compare_session_key: str, session_obj: SessionBase
    ):
        if compare_session_key not in session_obj:
            session_obj[compare_session_key] = []

    @classmethod
    def _check_if_item_exist_in_compare_session(
        cls, item_slug: str, compare_session_key: str, session_obj: SessionBase
    ) -> bool:
        if item_slug in session_obj[compare_session_key]:
            cls.delete_item_from_compare(item_slug, compare_session_key, session_obj)
            return True
        return False

    @classmethod
    def _change_max_len_of_session_list(
        cls, item_len: int, compare_session_key: str, session_obj: SessionBase
    ):
        if len(session_obj[compare_session_key]) > item_len:
            session_obj[compare_session_key].pop()

    @classmethod
    def sort_by_add_to_list(
        cls,
        compare_queryset: Iterable[QuerySet],
        session_obj: SessionBase,
        compare_session_key: str,
    ) -> Iterable[QuerySet]:
        sorted_queryset = sorted(
            compare_queryset,
            key=lambda x: session_obj[compare_session_key].index(x.slug),
        )
        return sorted_queryset

    @classmethod
    def add_item_to_compare(
        cls, item_slug: str, compare_session_key: str, session_obj: SessionBase
    ) -> str:
        status: str = None
        cls._check_if_session_dict_exist(compare_session_key, session_obj)
        is_in_list = cls._check_if_item_exist_in_compare_session(
            item_slug, compare_session_key, session_obj
        )
        status = "warning" if is_in_list else "success"
        session_obj[compare_session_key].insert(0, item_slug)

        cls._change_max_len_of_session_list(4, compare_session_key, session_obj)
        session_obj.modified = True
        return status

    @classmethod
    def delete_item_from_compare(
        cls, item_slug: str, compare_session_key: str, session_obj: SessionBase
    ) -> None:
        session_obj[compare_session_key].remove(item_slug)
        session_obj.modified = True

    @classmethod
    def get_compare_items_quantity(
        cls, compare_session_key: str, session_obj: SessionBase
    ) -> int:
        cls._check_if_session_dict_exist(compare_session_key, session_obj)
        compare_items_quantity = int(len(session_obj[compare_session_key]))
        return compare_items_quantity

    @classmethod
    def get_compare_list_items(
        cls, compare_session_key: str, session_obj: SessionBase
    ) -> list[str]:
        cls._check_if_session_dict_exist(compare_session_key, session_obj)
        compare_list = list(session_obj[compare_session_key])
        return compare_list


def add_message_to_front(data: dict, status: str, request) -> list[dict]:
    message = (
        _("Item {} is added to comparison").format(data["item_slug"])
        if status == "success"
        else _("Item {} is already in comparison set").format(data["item_slug"])
    )
    mes_success = messages.SUCCESS
    mes_warning = messages.WARNING
    messages.add_message(
        request,
        level=mes_success if status == "success" else mes_warning,
        message=message,
    )

    django_messages = []
    for message in messages.get_messages(request):
        django_messages.append(
            {
                "level": message.level,
                "message_text": message.message,
                "tags": message.tags,
            }
        )
    return django_messages


# TODO: навесить добавление в список сравнения на все карточки
