from django.contrib import admin
from .models import Sale, SaleItem
from productsApp.models import Product
from customerApp.models import Customer, Pio
from django.db import transaction


# Inline class to manage SaleItem within Sale
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1  # Number of empty forms to show by default
    fields = ['product', 'quantity', 'sell_price', 'total_price', 'profit_per_item', 'total_profit']
    readonly_fields = ['total_price', 'profit_per_item', 'total_profit']

    def get_queryset(self, request):
        # Override this method to make the total price and profit fields read-only
        return super().get_queryset(request).select_related('product')


# Admin class for Sale
class SaleAdmin(admin.ModelAdmin):
    list_display = ['customer', 'pio_number', 'total_sell_price', 'total_profit', 'created_at', 'updated_at']
    list_filter = ['customer', 'created_at']
    search_fields = ['customer__name', 'pio_number__number']
    readonly_fields = ['total_sell_price', 'total_profit', 'created_at', 'updated_at']
    inlines = [SaleItemInline]

    def save_model(self, request, obj, form, change):
        # Save the Sale instance first to generate the primary key
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        # Save the Sale instance and its related objects
        super().save_related(request, form, formsets, change)

        # Now that the Sale instance has a primary key, update related calculations
        obj = form.instance
        total_sell_price = sum(item.total_price for item in obj.items.all() if item.total_price is not None)
        total_profit = sum(item.total_profit for item in obj.items.all() if item.total_profit is not None)

        # Update the Sale instance with total sell price and profit
        obj.total_sell_price = total_sell_price
        obj.total_profit = total_profit
        obj.save(update_fields=['total_sell_price', 'total_profit'])

        # Update related Pio instance with the correct amount
        if obj.pio_number:
            obj.pio_number.total_amount = obj.total_sell_price if obj.total_sell_price else 0
            if obj.customer:
                if obj.customer.category == 'buyer':
                    obj.pio_number.buyer_due = obj.total_sell_price
                else:
                    obj.pio_number.seller_due = obj.total_sell_price
            obj.pio_number.save(update_fields=['total_amount', 'buyer_due', 'seller_due'])

        # Update customer's total due based on all purchases
        if obj.customer:
            obj.customer.total_due = sum(s.total_sell_price for s in obj.customer.sales.all())
            obj.customer.save(update_fields=['total_due'])
# Admin class for SaleItem
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'quantity', 'sell_price', 'total_price', 'total_profit']
    list_filter = ['sale', 'product']
    search_fields = ['product__name']
    readonly_fields = ['total_price', 'total_profit']

    def save_model(self, request, obj, form, change):
        # Override save method to calculate total price and profit when saving
        if obj.quantity and obj.sell_price:
            obj.total_price = obj.quantity * obj.sell_price
            if obj.product:
                obj.total_profit = obj.quantity * (obj.sell_price - obj.product.purchase_price)
        obj.save()

        # Update the product stock if the product exists
        if obj.product and obj.quantity:
            obj.product.stock -= obj.quantity or 0
            obj.product.save(update_fields=['stock'])


# Registering models in the admin site
admin.site.register(Sale, SaleAdmin)
admin.site.register(SaleItem, SaleItemAdmin)
