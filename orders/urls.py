from django.urls import path
from . import views
app_name = "orders"

urlpatterns=[
    path("pos/", views.pos_screen, name="pos_screen"),
    path("order/<int:pk>/", views.order_detail, name="order_detail"),
    path("order/<int:pk>/track/", views.track_order, name="track_order"),
]