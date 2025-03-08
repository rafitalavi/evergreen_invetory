from django import forms
from .models import Customer ,Transaction

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name' , 'category','total_due']
       

    # Optional: Custom validation for due_amount (if needed)
    def clean_due_amount(self):
        due_amount = self.cleaned_data.get('due_amount')
        if due_amount < 0:
            raise forms.ValidationError('Due amount cannot be negative')
        return due_amount
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'bank_name', 'discount', 'transaction_id']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
        }