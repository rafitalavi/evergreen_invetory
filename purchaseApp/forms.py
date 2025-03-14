from django import forms
from django.forms import inlineformset_factory
from .models import Purchase, PurchaseItem
from productsApp.models import Product
from customerApp.models import Customer ,Pio
class PioForm(forms.ModelForm):
    class Meta:
        model = Pio
        fields = ['pio_number', 'customer']
class PurchaseForm(forms.ModelForm):
      # Or form # User inputs PIO number manually

    class Meta:
        model = Purchase
        fields = ['customer', 'pio_number']
   
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            # Customize the queryset for the 'customer' field
            self.fields['customer'].queryset = Customer.objects.filter(category='seller')  # Example: show only buyers
 # Modify this as needed
    # def clean_pio_number(self):
    #     pio_number = self.cleaned_data.get('pio_number')
    #     if Pio.objects.filter(pio_number=pio_number).exists():  # Check if PIO number already exists
    #         raise forms.ValidationError('This PIO number already exists.')
    #     return pio_number
class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['id', 'product', 'quantity', 'buy_price']
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        buy_price = cleaned_data.get('buy_price')

        if quantity is None or quantity <= 0:
            self.add_error('quantity', "Quantity must be greater than 0.")
        if buy_price is None or buy_price <= 0:
            self.add_error('buy_price', "Buy Price must be greater than 0.")

        return cleaned_data