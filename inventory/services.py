from .models import Recipe
from accounts.models import User
from notifications.models import Notification

def adjust_inventory(food, quantity_delta):
    """Adjust ingredient stock for a change in ordered quantity of `food`.
    Positive quantity_delta = more consumed (deduct). Negative = less consumed (restock).
    """
    if not quantity_delta:
        return

    for recipe in Recipe.objects.filter(food=food):
        ingredient = recipe.ingredient
        change = recipe.quantity_required * quantity_delta
        ingredient.quantity = max(ingredient.quantity - change, 0)
        ingredient.save(update_fields=["quantity"])
        if quantity_delta > 0 and ingredient.is_low_stock:
            _notify_low_stock(ingredient)


def _notify_low_stock(ingredient):
    for manager in User.objects.filter(role=User.Role.MANAGER):
        Notification.objects.create(
            recipient=manager,
            notification_type=Notification.Type.LOW_STOCK,
            message=f"{ingredient.name} is low on stock ({ingredient.quantity} {ingredient.unit} left).",
        )