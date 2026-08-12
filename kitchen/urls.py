from django.urls import path
from . import views
app_name = "kitchen"

urlpatterns = [
    path("", views.kitchen_dashboard, name="dashboard"),
    path("start/<int:pk>/", views.start_cooking, name="start_cooking"),
    path("ready/<int:pk>/", views.mark_ready, name="mark_ready"),
]