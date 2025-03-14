from django.db import models, transaction
from productsApp.models import Product
from customerApp.models import Customer, Pio
import uuid
from django.core.exceptions import ValidationError


class Sale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, related_name="sales", null=True, blank=True)
    pio_number = models.ForeignKey(Pio, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    total_sell_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Save the Sale instance first to generate a primary key
            super().save(*args, **kwargs)

            # Calculate total_sell_price and total_profit from SaleItems
            total_sell_price = sum(item.total_price for item in self.items.all() if item.total_price is not None)
            total_profit = sum(item.total_profit for item in self.items.all() if item.total_profit is not None)

            # Create a new Pio instance if it's not already set
            if not self.pio_number:
                self.pio_number = Pio.objects.create(total_amount=0, buyer_due=0, seller_due=0)

            # Update the total_sell_price and total_profit fields
            self.total_sell_price = total_sell_price or 0
            self.total_profit = total_profit or 0

            # Save the Sale instance again to update the calculated fields
            super().save(*args, **kwargs)

            # Update the Pio instance with the correct amount
            if self.pio_number:
                self.pio_number.total_amount = self.total_sell_price

                if self.customer:
                    if self.customer.category == 'buyer':
                        self.pio_number.buyer_due = self.total_sell_price
                    else:
                        self.pio_number.seller_due = self.total_sell_price

                self.pio_number.save(update_fields=['total_amount', 'buyer_due', 'seller_due'])

            # Update customer's total due based on all purchases
            if self.customer:
                self.customer.total_due += self.total_sell_price
                self.customer.save(update_fields=['total_due'])


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, related_name="items", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    profit_per_item = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Calculate total_price, profit_per_item, and total_profit
            self.total_price = (self.quantity or 0) * (self.sell_price or 0)
            if self.product:
                self.profit_per_item = (self.sell_price or 0) - (self.product.purchase_price or 0)
                self.total_profit = (self.quantity or 0) * self.profit_per_item
            else:
                self.profit_per_item = None
                self.total_profit = None

            # Call the superclass save method
            super().save(*args, **kwargs)

            # Update the product stock if the product exists
            if self.product and self.quantity:
                self.product.stock -= self.quantity or 0
                self.product.save(update_fields=['stock'])