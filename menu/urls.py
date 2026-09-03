from django.urls import path
from . import views
app_name = "menu"

urlpatterns = [
    path("manage/", views.menu_manage, name="menu_manage"),
    path("category/add/", views.add_category, name="add_category"),
    path("item/add/", views.add_food_item, name="add_food_item"),
    path("item/<int:pk>/edit/", views.edit_food_item, name="edit_food_item"),
    path("item/<int:pk>/delete/", views.delete_food_item, name="delete_food_item"),
]