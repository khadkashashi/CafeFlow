from django.db import models
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    cost_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    image = models.ImageField(upload_to="food_items/", blank=True, null=True)
    preparation_time = models.PositiveIntegerField(help_text="Minutes", default=10)
    is_available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    calories = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} — Rs.{self.price}"

    @property  #Decorator -->The @property decorator tells Python to treat this method like a regular attribute (a property) instead of a callable function.
    def profit_margin(self):
        if self.price:
            return round(((self.price - self.cost_price) / self.price) * 100, 2) #round(..., 2)
        return 0