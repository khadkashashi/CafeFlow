from django.urls import path
from . import views
app_name = "customers"

urlpatterns = [
    path("", views.my_account, name="my_account"),
]