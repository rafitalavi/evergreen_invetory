from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from productsApp.models import Product
from customerApp.models import Customer, Pio
from .models import Sale, SaleItem

class PioForm(forms.ModelForm):
    class Meta:
        model = Pio
        fields = ['pio_number', 'customer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(category='buyer')

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'pio_number']

    def clean(self):
        cleaned_data = super().clean()
        customer = cleaned_data.get('customer')
        
        if customer and customer.total_due is None:
            raise ValidationError("Customer's total due field must be initialized.")
        
        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            sale = super().save(commit=False)
            sale.save()
            return sale


class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['sale', 'product', 'quantity', 'sell_price']

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        if product and quantity is not None:
            if product.stock < quantity or quantity <= 0:
                raise ValidationError(f"Not enough stock for {product.name}. Available stock: {product.stock}")
        
        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            sale_item = super().save(commit=False)
            sale_item.save()
            return sale_item
