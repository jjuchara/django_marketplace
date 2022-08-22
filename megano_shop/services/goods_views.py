from django.http import HttpResponse

# Добавьте сервис добавления в список просмотренных товаров, создайте методы-заглушки для работы этого сервиса.
# Сервис должен позволять:


class GoodsViewsService:
    @classmethod
    def get_viewed_list(cls, user_id):
        # получить список просмотренных товаров
        return HttpResponse(f"<h1>User {user_id} list of viewed goods</h1>")

    @classmethod
    def add_to_viewed(cls, user_id, goods_id):
        # добавить товар к списку просмотренных товаров
        return HttpResponse(
            f"<h1>Adding item {goods_id} to user {user_id} viewed goods list</h1>"
        )

    @classmethod
    def get_viewed_number(cls, user_id):
        # получить количество просмотренных товаров
        return HttpResponse(f"<h1>User {user_id} number of viewed goods</h1>")

    @classmethod
    def delete_from_viewed(cls, user_id, goods_id):
        # удалить товар из списка просмотренных товаров
        return HttpResponse(
            f"<h1>Item {goods_id} deleting from user {user_id} viewed goods list</h1>"
        )

    @classmethod
    def is_viewed(cls, user_id, goods_id):
        # узнать, есть ли товар уже в списке просмотренных
        return HttpResponse(
            f"<h1>Learning if item {goods_id} is in user {user_id} viewed goods list</h1>"
        )
