from django.urls import path
from . import views
app_name = "inventory"

urlpatterns = [
    path("", views.ingredient_list, name="ingredient_list"),
    path("add/", views.add_ingredient, name="add_ingredient"),
    path("<int:pk>/edit/", views.edit_ingredient, name="edit_ingredient"),
    path("purchase/", views.record_purchase, name="record_purchase"),
    path("recipes/", views.recipe_menu, name="recipe_menu"),
    path("recipes/<int:food_id>/", views.manage_recipe, name="manage_recipe"),
]