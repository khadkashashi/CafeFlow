from django.urls import path
from . import views
app_name = "landing"

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/", views.menu_page, name="menu"),
    path("table/<int:table_id>/menu/", views.table_menu, name="table_menu"),
    path("order/<int:order_pk>/review/", views.leave_review, name="leave_review"),
    path("review/", views.public_review, name="public_review"),

]