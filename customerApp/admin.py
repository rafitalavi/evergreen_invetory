from django.contrib import admin
from .models import Customer, Pio, Transaction, PaymentRecord

# Customizing Customer model admin
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'total_paid', 'total_due', 'created_at', 'updated_at')
    search_fields = ('name', 'category')
    list_filter = ('category', 'created_at', 'updated_at')
    ordering = ('-created_at',)  # To display latest first

admin.site.register(Customer, CustomerAdmin)


# Customizing Pio model admin
class PioAdmin(admin.ModelAdmin):
    list_display = ('pio_number', 'customer','total_amount', 'buyer_due', 'seller_due', 'created_at', 'updated_at')
    search_fields = ('pio_number', 'customer__name')
    list_filter = ('customer__category', 'created_at', 'updated_at')
    ordering = ('-created_at',)  # To display latest first

admin.site.register(Pio, PioAdmin)


# Customizing Transaction model admin
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'pio', 'customer', 'amount', 'transaction_type', 'created_at', 'updated_at')
    search_fields = ('transaction_id', 'customer__name', 'pio__pio_number')
    list_filter = ('transaction_type', 'customer__category', 'created_at', 'updated_at')
    ordering = ('-created_at',)  # To display latest first

admin.site.register(Transaction, TransactionAdmin)


# Customizing PaymentRecord model admin
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'amount_paid', 'discount', 'created_at')
    search_fields = ('transaction__transaction_id', 'transaction__pio__pio_number')
    list_filter = ('created_at',)
    ordering = ('-created_at',)  # To display latest first

admin.site.register(PaymentRecord, PaymentRecordAdmin)
