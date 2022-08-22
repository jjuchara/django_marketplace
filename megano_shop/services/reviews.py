from megano_shop.forms import ReviewsForm
from megano_shop.models import Item, Reviews


class ReviewsService:
    count_review = 10

    @classmethod
    def get_reviews_list(cls, goods_id, request):
        if request.GET.get("show_more"):
            cls.count_review += 10
            reviews = (
                Reviews.objects.filter(item=goods_id)
                .select_related("user")
                .order_by("-created_on")[: cls.count_review]
            )
        else:
            reviews = (
                Reviews.objects.filter(item=goods_id)
                .select_related("user")
                .order_by("-created_on")[:10]
            )
            cls.count_review = 10

        return reviews

    @classmethod
    def get_count_reviews(cls, goods_id):
        count = len(Reviews.objects.filter(item=goods_id))
        return count

    @classmethod
    def post_review(cls, goods_id, request):
        current_item = Item.objects.get(id=goods_id)
        reviews_form = ReviewsForm(
            request.POST, initial={"user": request.user.id, "item": current_item}
        )
        if reviews_form.is_valid():
            reviews_form.save()
        return reviews_form

        # добавление отзыва
        # return HttpResponse(f'<h1>Item {goods_id} Add Review Page</h1>')
