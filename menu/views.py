from accounts.decorators import role_required
from accounts.models import User
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CategoryForm, FoodItemForm
from .models import Category, FoodItem
from django.views.decorators.http import require_POST


@role_required(User.Role.MANAGER)
def menu_manage(request):
    categories = Category.objects.prefetch_related("items").all()
    return render(request, "menu/menu_manage.html", {"categories": categories})


@role_required(User.Role.MANAGER)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("menu:menu_manage")
    else:
        form = CategoryForm()
    return render(request, "menu/category_form.html", {"form": form})


@role_required(User.Role.MANAGER)
def add_food_item(request):
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("menu:menu_manage")
    else:
        form = FoodItemForm()
    return render(request, "menu/food_item_form.html", {"form": form})


@role_required(User.Role.MANAGER)
def edit_food_item(request, pk):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            form.save()
            return redirect("menu:menu_manage")
    else:
        form = FoodItemForm(instance=food)
    return render(request, "menu/food_item_form.html", {"form": form})


@role_required(User.Role.MANAGER)
@require_POST
def delete_food_item(request, pk):
    food = get_object_or_404(FoodItem, pk=pk)
    food.is_available = not food.is_available
    food.save(update_fields=["is_available"])
    return redirect("menu:menu_manage")