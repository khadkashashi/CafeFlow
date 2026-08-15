from django.urls import path
from . import views
app_name = "landing"

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/", views.menu_page, name="menu"),
]