"""Unlike everything else so far, the cart itself shouldn't be a database model — it's temporary, per-browser-session data that only becomes real once checkout converts it into an actual Order. Storing it in Django's session is the standard approach and avoids polluting your database with abandoned carts."""
from decimal import Decimal
from menu.models import FoodItem

class Cart:
    SESSION_KEY = "cart"
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if cart is None:
            cart = self.session[self.SESSION_KEY] = {}
        self.cart = cart

    def add(self, food_id, quantity=1):
        food_id = str(food_id)
        if food_id in self.cart:
            self.cart[food_id]["quantity"] += quantity
        else:
            self.cart[food_id] = {"quantity": quantity}
        self.save()

    def remove(self, food_id):
        food_id = str(food_id)
        if food_id in self.cart:
            del self.cart[food_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.save()

    def __iter__(self):
        food_ids = self.cart.keys()
        foods = FoodItem.objects.filter(id__in=food_ids)
        food_map = {str(f.id): f for f in foods}

        for food_id, item in self.cart.items():
            food = food_map.get(food_id)
            if not food:
                continue
            yield {
                "food": food,
                "quantity": item["quantity"],
                "line_total": food.price * item["quantity"],
            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    @property
    def total(self):
        return sum((item["food"].price * item["quantity"] for item in self), Decimal("0.00"))