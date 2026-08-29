from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_required
from accounts.models import User
from .forms import IngredientForm, PurchaseForm,SupplierForm
from .models import Ingredient, Purchase, Supplier
from menu.models import FoodItem
from .forms import RecipeFormSet
#create your views here

@role_required(User.Role.CHEF, User.Role.MANAGER)
def ingredient_list(request):
    ingredients = Ingredient.objects.select_related("supplier").all()
    can_edit = request.user.can_manage_inventory
    return render(request, "inventory/ingredient_list.html", {"ingredients": ingredients, "can_edit": can_edit})

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

@role_required(User.Role.MANAGER)
def recipe_menu(request):
    query = request.GET.get("q", "").strip()
    foods = FoodItem.objects.prefetch_related("recipe_items").all()
    if query:
        foods = foods.filter(name__icontains=query)
    return render(request, "inventory/recipe_menu.html", {"foods": foods, "query": query})

@role_required(User.Role.MANAGER)
def manage_recipe(request, food_id):
    food = get_object_or_404(FoodItem, pk=food_id)
    if request.method == "POST":
        if "add_ingredient" in request.POST:
            # Quick-create a brand-new ingredient without leaving this page
            new_form = IngredientForm(request.POST)
            if new_form.is_valid():
                new_form.save()
            formset = RecipeFormSet(instance=food)  # reload so the new ingredient shows in the dropdown
        else:
            formset = RecipeFormSet(request.POST, instance=food)
            if formset.is_valid():
                formset.save()
                return redirect("inventory:recipe_menu")
    else:
        formset = RecipeFormSet(instance=food)
    new_ingredient_form = IngredientForm()
    return render(request,"inventory/manage_recipe.html",{"food": food, "formset": formset, "new_ingredient_form": new_ingredient_form})

@role_required(User.Role.MANAGER)
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, "inventory/supplier_list.html", {"suppliers": suppliers})


@role_required(User.Role.MANAGER)
def add_supplier(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventory:supplier_list")
    else:
        form = SupplierForm()
    return render(request, "inventory/supplier_form.html", {"form": form})


@role_required(User.Role.MANAGER)
def edit_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect("inventory:supplier_list")
    else:
        form = SupplierForm(instance=supplier)
    return render(request, "inventory/supplier_form.html", {"form": form})


@role_required(User.Role.MANAGER)
def purchase_history(request):
    purchases = Purchase.objects.select_related("ingredient", "supplier").order_by("-date")
    return render(request, "inventory/purchase_history.html", {"purchases": purchases})