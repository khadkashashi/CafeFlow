from django.db import models

# Create your models here.
class Review(models.Model):
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="reviews")
    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="review", null=True, blank=True)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer} - {self.rating} Stars"