from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # fields = ['name', 'purchase_price', 'stock']
        fields = ['name' ,'stock', 'purchase_price']