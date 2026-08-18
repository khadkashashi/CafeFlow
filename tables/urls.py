from django.urls import path
from . import views
app_name = "tables"

urlpatterns = [
    path("", views.reception_dashboard, name="reception_dashboard"),
    path("table/<int:pk>/", views.table_detail, name="table_detail"),
    path("table/<int:pk>/start/", views.start_order, name="start_order"),
    path("order/<int:pk>/add-item/", views.add_item_to_order, name="add_item_to_order"),
    path("order/<int:pk>/send/", views.send_order_to_kitchen, name="send_order_to_kitchen"),
]