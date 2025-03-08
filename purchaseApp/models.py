# from django.db import models
# from productsApp.models import Product
# class Purchase(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="purchases", null=True, blank=True)
#     pio_number = models.OneToOneField( on_delete=models.CASCADE, null=True, blank=True)  # One PIO per purchase
#     total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#     updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

#     def save(self, *args, **kwargs):
      

#         super().save(*args, **kwargs)

#         # Calculate total price after saving PurchaseItems
#         self.total_price = sum(item.total_price for item in self.items.all())
#         super().save(update_fields=['total_price'])  # Update only total_price

#         if self.customer:
#             # Add PIO to customer's history (assuming ManyToManyField for multiple PIOs)
#             self.customer.pio_numbers.add(self.pio_number)

#             # Update the customer's due amount
#             self.customer.due_amount = (self.customer.due_amount or 0) + self.total_price
#             self.customer.save()

#             # Update customer category
#             self.customer.update_category()

#     def __str__(self):
#         return f"Purchase {self.pio_number.number if self.pio_number else 'N/A'} - {self.customer.name if self.customer else 'Unknown Customer'}"
# class PurchaseItem(models.Model):
#     purchase = models.ForeignKey("Purchase", on_delete=models.CASCADE, related_name="items", null=True, blank=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
#     quantity = models.PositiveIntegerField(null=True, blank=True)
#     buy_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Buy price per unit
#     total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)

#     def save(self, *args, **kwargs):
#         if self.quantity and self.buy_price:
#             self.total_price = self.quantity * self.buy_price  # Calculate total price
#         super().save(*args, **kwargs)

#         # Update product price and stock
#         if self.product:
#             if self.buy_price:
#                 self.product.purchase_price = self.buy_price  # Update latest buy price
#             if self.quantity:
#                 self.product.stock += self.quantity  # Increase stock
#             self.product.save()        