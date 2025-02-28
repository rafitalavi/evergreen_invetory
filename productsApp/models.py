from django.db import models
from categoryApp.models import Category 

from django.db import models
from categoryApp.models import Category  # Import Category from the correct app

class Product(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)  # Related Category
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Set when product is first created
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)  # Update every time the product is modified

    def __str__(self):
        return self.name
