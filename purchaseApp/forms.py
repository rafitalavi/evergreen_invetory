from django import forms
from .models import Purchase, PurchaseItem
from productsApp.models import Product
from customerApp.models import Customer ,Pio
class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['customer', 'pio_number', 'total_price']  # Add or remove fields as needed
        widgets = {
            'created_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'updated_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Automatically assign a new PIO if no PIO exists
        if not self.instance.pk and not self.instance.pio_number:
            self.instance.pio_number = Pio.objects.create(total_amount=None, buyer_due=None, seller_due=None)
            
        if 'customer' in self.fields:
            self.fields['customer'].queryset = Customer.objects.all()
            
    def clean(self):
        cleaned_data = super().clean()
        total_price = cleaned_data.get('total_price')

        # Calculate total_price if not provided and items exist
        if not total_price:
            self.instance.total_price = sum(item.total_price for item in self.instance.items.all())
        
        return cleaned_data

class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['purchase', 'product', 'quantity', 'buy_price', 'total_price']
        widgets = {
            'total_price': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure 'purchase' is read-only if already part of the form (e.g., when editing)
        if 'purchase' in self.initial:
            self.fields['purchase'].widget.attrs['readonly'] = 'readonly'

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        buy_price = cleaned_data.get('buy_price')
        
        if quantity and buy_price:
            cleaned_data['total_price'] = quantity * buy_price
        else:
            raise forms.ValidationError("Quantity and Buy Price must be provided.")

        return cleaned_data
