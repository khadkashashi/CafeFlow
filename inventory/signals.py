from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import OrderItem
from .services import adjust_inventory


@receiver(post_save, sender=OrderItem)
def deduct_ingredients_on_order(sender, instance, created, **kwargs):
    if created:
        adjust_inventory(instance.food, instance.quantity)