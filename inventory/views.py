from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_required
from accounts.models import User
from .forms import IngredientForm, PurchaseForm
from .models import Ingredient, Purchase
#create your views here

@role_required(User.Role.MANAGER)
def ingredient_list(request):
    ingredients = Ingredient.objects.select_related("supplier").all()
    return render(request, "inventory/ingredient_list.html", {"ingredients": ingredients})

@role_required(User.Role.MANAGER)
def add_ingredient(request):
    if request.method == "POST":
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventory:ingredient_list")
    else:
        form = IngredientForm()
    return render(request, "inventory/ingredient_form.html", {"form": form})


@role_required(User.Role.MANAGER)
def edit_ingredient(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    if request.method == "POST":
        form = IngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            form.save()
            return redirect("inventory:ingredient_list")
    else:
        form = IngredientForm(instance=ingredient)
    return render(request, "inventory/ingredient_form.html", {"form": form})


@role_required(User.Role.MANAGER)
def record_purchase(request):
    if request.method == "POST":
        form = PurchaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventory:ingredient_list")
    else:
        form = PurchaseForm()
    return render(request, "inventory/purchase_form.html", {"form": form})