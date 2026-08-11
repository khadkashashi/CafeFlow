from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import Notification
from orders.models import OrderItem
from .models import Ingredient, Recipe

User = get_user_model()
@receiver(post_save, sender=OrderItem)
def deduct_ingredients_on_order(sender, instance, created, **kwargs):
    if not created:
        return

    recipes = Recipe.objects.filter(food=instance.food)
    for recipe in recipes:
        ingredient = recipe.ingredient
        needed = recipe.quantity_required * instance.quantity
        ingredient.quantity = max(ingredient.quantity - needed, 0)
        ingredient.save(update_fields=["quantity"])

        if ingredient.is_low_stock:
            notify_low_stock(ingredient)


def notify_low_stock(ingredient):
    managers = User.objects.filter(role=User.Role.MANAGER)
    for manager in managers:
        Notification.objects.create(
            recipient=manager,
            notification_type=Notification.Type.LOW_STOCK,
            message=f"{ingredient.name} is low on stock ({ingredient.quantity} {ingredient.unit} left).",
        )