from django.shortcuts import render
from menu.models import Category, FoodItem
from landing.models import Review

# Create your views here.
def home(request):
    featured = FoodItem.objects.filter(is_available=True).select_related("category")[:3]
    reviews = Review.objects.select_related("customer").order_by("created_at")[:4]
    context = {
        "reviews": reviews,
        "featured": featured
    }

    return render(request,"landing/home.html",context)


def menu_page(request):
    categories = Category.objects.prefetch_related("items").all()
    return render(request, "landing/menu.html", {"categories": categories})

"""prefetch_related("items") here is the sibling of select_related from the kitchen dashboard — same N+1 problem, different fix. select_related does a SQL JOIN (good for ForeignKey/OneToOne — "one row per match"). prefetch_related runs a second separate query and joins in Python (needed here because Category → FoodItem is a reverse FK / one-to-many — a JOIN would duplicate the category row per food item, so Django fetches both querysets and stitches them together instead). Worth knowing which one applies when, since picking the wrong one either breaks or just silently under-performs."""