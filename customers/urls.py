from django.urls import path
from . import views
app_name = "customers"

urlpatterns = [
    path("", views.my_account, name="my_account"),
    path("check-points/", views.check_points, name="check_points"),
]