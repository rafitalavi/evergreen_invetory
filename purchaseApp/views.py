from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.forms import modelformset_factory
from .models import Purchase, PurchaseItem
from productsApp.models import Product
from customerApp.models import Customer, Pio
from .forms import   PurchaseForm ,PurchaseItemForm , PioForm




def purchase_create(request, pio_id=None):
    PurchaseItemFormSet = modelformset_factory(PurchaseItem, form=PurchaseItemForm, extra=1)
    pio = None
    customer = None

    # Fetch existing PIO and customer if `pio_id` is provided
    if pio_id:
        pio = get_object_or_404(Pio, id=pio_id)
        customer = pio.customer  

    if request.method == 'POST':
        if 'create_pio' in request.POST:  # Handling PIO form submission
            pio_form = PioForm(request.POST)
            if pio_form.is_valid():
                pio = pio_form.save()
                return redirect('purchase_create_with_pio', pio_id=pio.id)
        else:  # Handling Purchase and PurchaseItem formset submission
            form = PurchaseForm(request.POST)
            formset = PurchaseItemFormSet(request.POST)

            if form.is_valid() and formset.is_valid():
                customer = form.cleaned_data.get('customer')
                pio = pio or form.cleaned_data.get('pio_number')

                if customer and pio:
                    try:
                        with transaction.atomic():
                            # Create Purchase instance
                            purchase = form.save(commit=False)
                            purchase.pio_number = pio
                            purchase.save()

                            # Process PurchaseItem formset
                            total_price = 0
                            for item_form in formset:
                                if item_form.cleaned_data:
                                    product = item_form.cleaned_data['product']
                                    quantity = item_form.cleaned_data['quantity']
                                    buy_price = item_form.cleaned_data['buy_price']
                                    item_total = quantity * buy_price
                                    total_price += item_total

                                    PurchaseItem.objects.create(
                                        purchase=purchase,
                                        product=product,
                                        quantity=quantity,
                                        buy_price=buy_price,
                                        total_price=item_total
                                    )

                            # Update total price for purchase
                            purchase.total_price = total_price
                            purchase.save()

                            # Update related PIO and Customer due amounts
                            pio.total_amount = total_price
                            if customer.category == 'buyer':
                                pio.seller_due = total_price
                            else:
                                pio.buyer_due = total_price
                            pio.save()

                            # Update customer's total due
                            customer.total_due = sum(p.total_price for p in customer.purchases.all())
                            customer.save()

                        return redirect('purchase_list')

                    except Exception as e:
                        return JsonResponse({'error': str(e)}, status=400)

            return JsonResponse({'error': 'Invalid form data', 'form_errors': form.errors, 'formset_errors': formset.errors}, status=400)

    else:
        pio_form = PioForm()
        form = PurchaseForm(initial={'customer': customer, 'pio_number': pio})
        formset = PurchaseItemFormSet(queryset=PurchaseItem.objects.none())

    return render(request, 'purchaseApp/purchase_form.html', {
        'pio_form': pio_form,
        'form': form,
        'formset': formset,
        'pio': pio,
    })
# from django.shortcuts import render, redirect
# from .forms import PurchaseForm

# def purchase_create(request):
#     if request.method == 'POST':
#         form = PurchaseForm(request.POST)
#         if form.is_valid():
#             customer = form.cleaned_data.get('customer')  # Ensure this is assigned before using
#             if customer:
#                 # Proceed with the purchase creation logic
#                 form.save()
#                 return redirect('purchase_list')  # Redirect after successful save
#             else:
#                 # Handle the case where no customer is selected
#                 form.add_error('customer', 'Please select a customer.')
#     else:
#         form = PurchaseForm()

#     return render(request, 'purchaseApp/purchase_form.html', {'form': form})

def purchase_list(request):
    purchases = Purchase.objects.all().order_by('-created_at')
    return render(request, 'purchaseApp/purchase_list.html', {'purchases': purchases})
#details
def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    purchase_items = purchase.items.all()  # Get all purchase items
    return render(request, 'purchaseApp/purchase_detail.html', {'purchase': purchase, 'purchase_items': purchase_items})
#update perChase
# def purchase_update(request, pk):
#     purchase = get_object_or_404(Purchase, pk=pk)
#     PurchaseItemFormSet = modelformset_factory(PurchaseItem, form=PurchaseItemForm, extra=1, can_delete=True)
#     pio = purchase.pio_number
#     customer = purchase.customer

#     if request.method == 'POST':
#         if 'create_pio' in request.POST:  # Handling PIO form submission
#             pio_form = PioForm(request.POST)
#             if pio_form.is_valid():
#                 pio = pio_form.save()
#                 return redirect('purchase_update', pk=purchase.pk)
#         else:  # Handling Purchase and PurchaseItem formset submission
#             form = PurchaseForm(request.POST, instance=purchase)
#             formset = PurchaseItemFormSet(request.POST, queryset=PurchaseItem.objects.filter(purchase=purchase))

#             print("Form errors:", form.errors)
#             print("Formset errors:", formset.errors)

#             if form.is_valid() and formset.is_valid():
#                 customer = form.cleaned_data.get('customer')
#                 pio = pio or form.cleaned_data.get('pio_number')

#                 if customer and pio:
#                     try:
#                         with transaction.atomic():
#                             # Fetch old values
#                             old_total_price = purchase.total_price
#                             old_total_due = customer.total_due
#                             old_seller_due = pio.seller_due if customer.category == 'seller' else None
#                             old_buyer_due = pio.buyer_due if customer.category == 'buyer' else None

#                             # Update Purchase instance
#                             purchase = form.save(commit=False)
#                             purchase.pio_number = pio
#                             purchase.save()

#                             # Process PurchaseItem formset
#                             total_price = 0
#                             for item_form in formset:
#                                 if item_form.is_valid():  # Only process valid forms
#                                     if item_form.cleaned_data.get('DELETE'):
#                                         item_form.instance.delete()
#                                     else:
#                                         product = item_form.cleaned_data['product']
#                                         quantity = item_form.cleaned_data['quantity']
#                                         buy_price = item_form.cleaned_data['buy_price']
#                                         item_total = quantity * buy_price
#                                         total_price += item_total

#                                         item = item_form.save(commit=False)
#                                         item.purchase = purchase
#                                         item.total_price = item_total
#                                         item.save()

#                             # Update total price for purchase
#                             purchase.total_price = total_price
#                             purchase.save()

#                             # Calculate differences
#                             total_price_difference = total_price - old_total_price

#                             # Update customer's total due
#                             customer.total_due = old_total_due + total_price_difference
#                             customer.save(update_fields=['total_due'])

#                             # Update Pio's total_amount, seller_due, or buyer_due
#                             pio.total_amount = (pio.total_amount or 0) + total_price_difference

#                             if customer.category == 'buyer':
#                                 pio.buyer_due = (old_buyer_due or 0) + total_price_difference
#                             else:
#                                 pio.seller_due = (old_seller_due or 0) + total_price_difference

#                             pio.save(update_fields=['total_amount', 'seller_due', 'buyer_due'])

#                         return redirect('purchase_detail', pk=purchase.pk)

#                     except Exception as e:
#                         return JsonResponse({'error': str(e)}, status=400)

#             return JsonResponse({'error': 'Invalid form data', 'form_errors': form.errors, 'formset_errors': formset.errors}, status=400)

#     else:
#         form = PurchaseForm(instance=purchase)
#         formset = PurchaseItemFormSet(queryset=PurchaseItem.objects.filter(purchase=purchase))

#     return render(request, 'purchaseApp/purchase_update.html', {
#         'form': form,
#         'formset': formset,
#         'purchase': purchase,
#         'pio': pio,
#         'customer': customer,
#     })
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.db import transaction
from .models import Purchase
from .forms import PurchaseForm  # Assuming you have a form for updating Purchase

# Update view for the Purchase model
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction
from .models import Purchase, PurchaseItem
from .forms import PurchaseForm, PurchaseItemForm

def purchase_update(request, pk):
    purchase = get_object_or_404(Purchase, id=pk)
    purchase_items = purchase.items.all()

    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        item_forms = [PurchaseItemForm(request.POST, prefix=str(item.id), instance=item) for item in purchase_items]

        if form.is_valid() and all(item_form.is_valid() for item_form in item_forms):
            with transaction.atomic():
                total_price = 0

                # Loop through each item form and save only if it has changed
                for item_form in item_forms:
                    if item_form.has_changed():  # Check if the form has been edited
                        item = item_form.save(commit=False)
                        item.total_price = item_form.cleaned_data.get('total_price', 0)
                        item.save()  # Save the updated PurchaseItem
                        total_price += item.total_price  # Accumulate the total price

                # Update the total price for the Purchase itself
                old_total_price = purchase.total_price
                new_total_price = total_price or 0
                price_difference = new_total_price - old_total_price

                # Update the total price for the Purchase itself
                # purchase.total_price = new_total_price
                # form.save()
                purchase.total_price = total_price or 0
                form.save()

                # Update the related Pio instance
                if purchase.pio_number:
                    purchase.pio_number.total_amount = purchase.total_price
                    if purchase.customer:
                        if purchase.customer.category == 'buyer':
                            purchase.pio_number.buyer_due += (price_difference - purchase.pio_number.total_paid_pio)
                        else:
                            purchase.pio_number.seller_due += (price_difference - purchase.pio_number.total_paid_pio)
                    purchase.pio_number.save(update_fields=['total_amount', 'buyer_due', 'seller_due'])

                # Recalculate the customer's total due based on all purchases
                if purchase.customer:
                    customer = purchase.customer
                    pio = customer.pios.first()
                    # Recalculate total_due as the sum of all purchase total_prices
                    customer.total_due = sum(p.total_price for p in customer.purchases.all()) - pio.total_paid_pio
                    customer.save(update_fields=['total_due'])

                return redirect('purchase_detail', pk=purchase.id)  # Redirect to the updated purchase detail page

    else:
        form = PurchaseForm(instance=purchase)
        item_forms = [PurchaseItemForm(prefix=str(item.id), instance=item) for item in purchase_items]  # Initialize item forms for GET request

    return render(request, 'purchaseApp/update_purchase.html', {
        'form': form,
        'purchase': purchase,
        'purchase_items': purchase_items,
        'item_forms': item_forms  # Pass updated item forms to the template
    })

def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)

    if request.method == 'POST':
        purchase.delete()
        return redirect('purchase_list')

    return render(request, 'purchaseApp/purchase_confirm_delete.html', {'purchase': purchase})
# Create Purchase Item
def purchase_item_create(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)

    if request.method == 'POST':
        form = PurchaseItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.purchase = purchase
            item.total_price = item.quantity * item.buy_price
            item.save()
            return redirect('purchase_detail', pk=purchase.pk)
    else:
        form = PurchaseItemForm()

    return render(request, 'purchaseApp/purchase_item_form.html', {'form': form, 'purchase': purchase})

def purchase_item_update(request, pk):
    item = get_object_or_404(PurchaseItem, pk=pk)

    if request.method == 'POST':
        form = PurchaseItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('purchase_detail', pk=item.purchase.pk)
    else:
        form = PurchaseItemForm(instance=item)

    return render(request, 'purchaseApp/purchase_item_form.html', {'form': form})


def purchase_item_delete(request, pk):
    item = get_object_or_404(PurchaseItem, pk=pk)

    if request.method == 'POST':
        item.delete()
        return redirect('purchase_detail', pk=item.purchase.pk)

    return render(request, 'purchaseApp/purchase_item_confirm_delete.html', {'item': item})
