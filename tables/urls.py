from django.urls import path
from . import views
app_name = "tables"

urlpatterns = [
    path("", views.reception_dashboard, name="reception_dashboard"),
]