from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .models import KitchenOrder

@receiver(post_save, sender=Order)
def create_kitchen_ticket(sender, instance, created, **kwargs):
    if created:
        KitchenOrder.objects.create(order=instance)