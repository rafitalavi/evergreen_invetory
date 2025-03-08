from django.db import models
from django.db.models import Sum

class Customer(models.Model):
    CATEGORY_CHOICES = [
        ("buyer", "Buyer"),
        ("seller", "Seller"),
        ("wholesaler", "Wholesaler"),
        ("retailer", "Retailer"),
    ]

    id = models.AutoField(primary_key=True)  # Explicitly defining the ID
    name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="buyer", null=True, blank=True)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    total_due = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.category})" if self.name else "Unnamed Customer"

    def update_due_amount(self):
        """Update total_due and total_paid based on the customer's category."""
        # Aggregate total paid and total discount from related transactions
        total_paid_and_discount = self.transactions.aggregate(
            total_paid=Sum('amount'),
            total_discount=Sum('discount')
        )
        total_paid = total_paid_and_discount['total_paid'] or 0
        total_discount = total_paid_and_discount['total_discount'] or 0

        # # Calculate total_due based on customer category
        # if self.category == "buyer":
        #     # For buyers, sum up the buyer_due from related PIOs
        #     total_due = self.pios.aggregate(
        #         total_due=Sum('buyer_due')
        #     )['total_due'] or 0
        # elif self.category == "seller":
        #     # For sellers, sum up the seller_due from related PIOs
        #     total_due = self.pios.aggregate(
        #         total_due=Sum('seller_due')
        #     )['total_due'] or 0
        # else:
        #     # For other categories (e.g., wholesaler, retailer), sum both buyer_due and seller_due
        #     total_due = self.pios.aggregate(
        #         total_due=Sum('buyer_due') + Sum('seller_due')
        #     )['total_due'] or 0

        # Update the customer's total_paid and total_due fields
        self.total_paid = total_paid - total_discount
        # self.total_due = total_due 

        self.save()

class Pio(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="pios", null=True, blank=True)
    pio_number = models.CharField(max_length=50, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    buyer_due = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    seller_due = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.pio_number} ({self.customer.name})" if self.pio_number else "Unnamed PIO"

    def update_due(self):
        """Update due amounts for both buyer and seller."""
        print("Updating due for PIO:", self.pio_number)  # Debugging statement
        
        try:
            # Fetch all related transactions for the PIO
            total_paid_buyer = self.transactions.filter(transaction_type="sell").aggregate(
                total_paid=Sum("amount"),
                total_discount=Sum("discount"),
            ) or {"total_paid": 0, "total_discount": 0}

            total_paid_seller = self.transactions.filter(transaction_type="buy").aggregate(
                total_paid=Sum("amount"),
                total_discount=Sum("discount"),
            ) or {"total_paid": 0, "total_discount": 0}

            total_paid_buyer_amount = total_paid_buyer["total_paid"] or 0
            total_paid_seller_amount = total_paid_seller["total_paid"] or 0
            total_discount_buyer = total_paid_buyer["total_discount"] or 0
            total_discount_seller = total_paid_seller["total_discount"] or 0

            # Update due for buyer and seller
            self.buyer_due = max(0, self.buyer_due - (total_paid_buyer_amount - total_discount_buyer))
            self.seller_due = max(0, self.seller_due - (total_paid_seller_amount - total_discount_seller))
            
            print(f"Updated Buyer Due: {self.buyer_due}, Updated Seller Due: {self.seller_due}")

            self.save()

            # Removed self.customer.update_due_amount() to prevent updating the customer's due

        except Exception as e:
            print(f"Error updating due: {e}")


#### `Transaction` Model:

class Transaction(models.Model):
    BUY_SELL_CHOICES = [
        ("buy", "Buy"),
        ("sell", "Sell"),
    ]

    id = models.AutoField(primary_key=True)
    pio = models.ForeignKey(Pio, on_delete=models.CASCADE, related_name="transactions", null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="transactions", null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    transaction_type = models.CharField(max_length=5, choices=BUY_SELL_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.pio.pio_number} ({self.transaction_type})"

    def save(self, *args, **kwargs):
        """Automatically set transaction type and update due amounts."""
        if self.customer:
            if self.customer.category == "buyer":
                self.transaction_type = "sell"
            elif self.customer.category == "seller":
                self.transaction_type = "buy"
        
        super().save(*args, **kwargs)  # Save the transaction first

        # Ensure PIO exists before trying to update its due
        if self.pio:
            print(f"Saving Transaction for PIO {self.pio.pio_number}")

            # Subtract only the current transaction amount
            if self.transaction_type == "sell":
                self.pio.buyer_due = max(0, self.pio.buyer_due - self.amount)
            elif self.transaction_type == "buy":
                self.pio.seller_due = max(0, self.pio.seller_due - self.amount)

            self.pio.save()  # Save updated PIO dues

        # Update the customer's due amounts after transaction
        if self.customer:
            print(f"Saving Transaction for Customer {self.customer.name}")
            # Calculate total due after this transaction
            self.customer.total_due = max(
                0, 
                self.customer.total_due - (self.amount - self.discount)
            )
            self.customer.update_due_amount()  # Recalculate the customer’s total due

        # Update due for customer
        # if self.customer:
        #     print(f"Saving Transaction for Customer {self.customer.name}")
        #     self.customer.update_due_amount()
class PaymentRecord(models.Model):
    id = models.AutoField(primary_key=True)  # Explicitly defining the ID
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="payment_records", null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Time when payment was made

    def __str__(self):
        return f"Payment Record: {self.transaction.transaction_id} - {self.amount_paid} Paid"
