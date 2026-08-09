from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import OrderItem
from .models import Recipe


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