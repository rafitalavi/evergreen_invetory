from django.db import models, transaction
from productsApp.models import Product
from customerApp.models import Customer, Pio
import uuid  # To use UUID as a primary key
from django.core.exceptions import ValidationError

class Purchase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID as primary key
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, related_name="purchases", null=True, blank=True)
    pio_number = models.OneToOneField(Pio, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # If the instance is new, save it first to generate a primary key
            if not self.pk:
                super().save(*args, **kwargs)  

            # Now it's safe to access related PurchaseItems
            self.total_price = sum(item.total_price for item in self.items.all())

            # Create a new Pio instance if it's not already set
            if not self.pio_number:
                self.pio_number = Pio.objects.create(total_amount=None, buyer_due=None, seller_due=None)

            # Save the Purchase instance again to store total_price and pio_number
            super().save(*args, **kwargs)  

            # Update Pio instance with the correct amount
            if self.pio_number:
                self.pio_number.total_amount = self.total_price or 0

                if self.customer:
                    if self.customer.category == 'buyer':
                        self.pio_number.buyer_due = self.total_price or 0
                    else:
                        self.pio_number.seller_due = self.total_price or 0

                self.pio_number.save(update_fields=['total_amount', 'buyer_due', 'seller_due'])

                # Update customer's total due based on all purchases
                if self.customer:
                    # Assuming you're in a method where self refers to a Purchase or another model instance
                    self.customer.total_due +=self.total_price
                    self.customer.save()  # Save the updated total_due to the database

                    self.customer.save(update_fields=['total_due'])


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.SET_NULL, related_name="items", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Ensure the Purchase ID is a valid UUID
            if self.purchase and not isinstance(self.purchase.id, uuid.UUID):
                raise ValidationError("Invalid UUID format for Purchase ID")

            self.total_price = (self.quantity or 0) * (self.buy_price or 0)
            super().save(*args, **kwargs)

            if self.purchase:
                self.purchase.save()

            if self.product:
                if self.buy_price is not None:
                    self.product.purchase_price = self.buy_price  
                if self.quantity:
                    self.product.stock += self.quantity  
                self.product.save(update_fields=['purchase_price', 'stock'])