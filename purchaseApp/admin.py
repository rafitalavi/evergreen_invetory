from django.contrib import admin
from .models import Purchase, PurchaseItem
from productsApp.models import Product

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1  # Number of empty forms to show by default
    fields = ['product', 'quantity', 'buy_price', 'total_price']
    readonly_fields = ['total_price']

    def get_queryset(self, request):
        # Override this method to make the total price field read-only
        return super().get_queryset(request).select_related('product')

from django.db import transaction

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['customer', 'pio_number', 'total_price', 'created_at', 'updated_at']
    list_filter = ['customer', 'created_at']
    search_fields = ['customer__name', 'pio_number__number']  # Assuming 'name' and 'number' fields exist
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    inlines = [PurchaseItemInline]

    def save_model(self, request, obj, form, change):
        # Save the Purchase object first to generate the primary key
        with transaction.atomic():  # Wrap the save in a transaction to ensure consistency
            obj.save()  # Save the object first to generate the primary key
            # Update total price after saving all PurchaseItems
            obj.total_price = sum(item.total_price for item in obj.items.all())
            obj.save(update_fields=['total_price'])

            # Now, save any related PurchaseItem instances (after primary key is assigned)
            for item in obj.items.all():
                item.save()

        # Now, update the total amount in PIO and customer dues
        if obj.pio_number:
            obj.pio_number.total_amount = obj.total_price if obj.total_price is not None else None
            if obj.customer:
                if obj.customer.category == 'buyer':
                    obj.pio_number.seller_due = obj.total_price if obj.total_price is not None else None
                else:
                    obj.pio_number.buyer_due = obj.total_price if obj.total_price is not None else None
            obj.pio_number.save(update_fields=['total_amount', 'buyer_due', 'seller_due'])

            # Update customer's total due
            obj.customer.total_due = sum(p.total_price for p in obj.customer.purchases.all())
            obj.customer.save(update_fields=['total_due'])

class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ['purchase', 'product', 'quantity', 'buy_price', 'total_price']
    list_filter = ['purchase', 'product']
    search_fields = ['product__name']
    readonly_fields = ['total_price']

    def save_model(self, request, obj, form, change):
        # Override save method to calculate total price when saving
        if obj.quantity and obj.buy_price:
            obj.total_price = obj.quantity * obj.buy_price
        obj.save()

# Registering models in the admin site
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(PurchaseItem, PurchaseItemAdmin)
