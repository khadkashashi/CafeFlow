from django.urls import path
from . import views
app_name = "tables"

urlpatterns = [
    path("", views.reception_dashboard, name="reception_dashboard"),
    path("table/<int:pk>/", views.table_detail, name="table_detail"),
    path("table/<int:pk>/start/", views.start_order, name="start_order"),
    path("order/<int:pk>/add-item/", views.add_item_to_order, name="add_item_to_order"),
    path("order/<int:pk>/send/", views.send_order_to_kitchen, name="send_order_to_kitchen"),
    path("table/<int:pk>/clean/", views.mark_table_clean, name="mark_table_clean"),
    path("item/<int:item_pk>/remove/", views.remove_item_from_order, name="remove_item_from_order"),
    path("item/<int:item_pk>/update/", views.update_item_quantity, name="update_item_quantity"),
    path("order/<int:pk>/discount/", views.apply_discount, name="apply_discount"),
    path("waiter/", views.waiter_tables, name="waiter_tables"),
    path("table/<int:pk>/bill/", views.table_bill, name="table_bill"),
    path("table/<int:pk>/transfer/", views.transfer_order, name="transfer_order"),
    path("merge/", views.merge_tables, name="merge_tables"),
    path("manage/", views.table_manage, name="table_manage"),
    path("manage/add/", views.add_table, name="add_table"),
    path("manage/<int:pk>/edit/", views.edit_table, name="edit_table"),
    path("manage/<int:pk>/delete/", views.delete_table, name="delete_table"),
    
]