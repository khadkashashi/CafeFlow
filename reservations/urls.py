from django.urls import path
from . import views
app_name = "reservations"

urlpatterns = [
    path("new/", views.make_reservation, name="make_reservation"),
    path("mine/", views.my_reservations, name="my_reservations"),
    path("manage/", views.reservation_list, name="reservation_list"),
    path("manage/<int:pk>/confirm/", views.confirm_reservation, name="confirm_reservation"),
]