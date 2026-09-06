from django.urls import path
from . import views
app_name = "reports"

urlpatterns = [
    path("", views.reports_dashboard, name="dashboard"),
    path("profit-loss/", views.profit_loss, name="profit_loss"),
    ]