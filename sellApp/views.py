from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.forms import modelformset_factory
from purchaseApp.models import Purchase, PurchaseItem
from productsApp.models import Product
from customerApp.models import Customer, Pio
from .forms import SaleForm, SaleItemForm, PioForm
# from .forms import   PurchaseForm ,PurchaseItemForm , PioForm
from .models import Sale ,SaleItem

from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime

def sale_list(request):
    sales = Sale.objects.all().order_by('-created_at')

    # Get search query parameters
    search_pio = request.GET.get('pio_number', '')
    search_customer = request.GET.get('customer_name', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Filtering
    if search_pio:
        sales = sales.filter(pio_number__icontains=search_pio)
    if search_customer:
        sales = sales.filter(customer__name__icontains=search_customer)
    if start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            sales = sales.filter(created_at__range=[start_date_obj, end_date_obj])
        except ValueError:
            pass  # Ignore invalid date formats

    # Pagination (10 items per page)
    paginator = Paginator(sales, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'sellApp/sale_list.html', {
        'sales': page_obj,
        'search_pio': search_pio,
        'search_customer': search_customer,
        'start_date': start_date,
        'end_date': end_date,
    })
def sale_detail(request, pk):
    # Get the sale object by pk, or return a 404 if not found
    sale = get_object_or_404(Sale, pk=pk)
    
    # Calculate total profit
    total_profit = 0
    for item in sale.items.all():
        if item.buy_price is None:
            item.buy_price = 0  # or some default value like 0 or item.product.purchase_price
        if item.sell_price is None:
            item.sell_price = 0  # Default to 0 if not set
        profit = (item.sell_price - item.buy_price) * item.quantity  # Profit for each item
        total_profit += profit

    # Pass the sale object and total profit to the template context
    return render(request, 'sellApp/sale_detail.html', {'sale': sale, 'total_profit': total_profit})

from django.db import transaction

def sale_update(request, pk):
    sale = get_object_or_404(Sale, id=pk)
    previous_sale_items = {item.id: item for item in sale.items.all()}  # Store previous items

    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        item_forms = [SaleItemForm(request.POST, prefix=str(item.id), instance=item) for item in previous_sale_items.values()]

        if form.is_valid() and all(item_form.is_valid() for item_form in item_forms):
            with transaction.atomic():
                total_sell_price = 0
                total_profit = 0
                updated_items = set()  # Track updated item IDs

                # Process updated sale items
                for item_form in item_forms:
                    if item_form.has_changed():
                        item = item_form.save(commit=False)
                        updated_items.add(item.id)

                        # Adjust stock before updating quantity
                        old_item = previous_sale_items.get(item.id)
                        if old_item:
                            old_item.product.stock += old_item.quantity  # Restore old stock
                            old_item.product.save(update_fields=['stock'])

                        # Update item
                        item.total_price = item.quantity * item.sell_price if item.quantity and item.sell_price else 0
                        item.total_profit = item.quantity * (item.sell_price - item.buy_price) if item.quantity and item.sell_price and item.buy_price else 0
                        item.save()

                        # Deduct new quantity from stock
                        item.product.stock -= item.quantity
                        item.product.save(update_fields=['stock'])

                        total_sell_price += item.total_price
                        total_profit += item.total_profit

                # Restore stock for removed items
                for item_id, old_item in previous_sale_items.items():
                    if item_id not in updated_items:
                        old_item.product.stock += old_item.quantity  # Restore stock for deleted item
                        old_item.product.save(update_fields=['stock'])
                        old_item.delete()  # Remove item from sale

                # Update Sale instance
                sale.total_sell_price = total_sell_price
                sale.total_profit = total_profit
                form.save()

                # Update PIO and customer due amounts
                if sale.pio_number:
                    sale.pio_number.total_amount = sale.total_sell_price
                    if sale.customer:
                        if sale.customer.category == 'buyer':
                            sale.pio_number.buyer_due = sale.total_sell_price
                        else:
                            sale.pio_number.seller_due = sale.total_sell_price
                    sale.pio_number.save(update_fields=['total_amount', 'buyer_due', 'seller_due'])

                if sale.customer:
                    sale.customer.total_due = sum(s.total_sell_price for s in sale.customer.sales.all())
                    sale.customer.save(update_fields=['total_due'])

                return redirect('sale_detail', pk=sale.id)

    else:
        form = SaleForm(instance=sale)
        item_forms = [SaleItemForm(prefix=str(item.id), instance=item) for item in sale.items.all()]

    return render(request, 'sellApp/update_sale.html', {
        'form': form,
        'sale': sale,
        'item_forms': item_forms,
    })

def sale_delete(post,pk):
    pass
def sale_create(request, pio_id=None):
    SaleItemFormSet = modelformset_factory(SaleItem, form=SaleItemForm, extra=1)
    pio = None
    customer = None

    if pio_id:
        pio = get_object_or_404(Pio, id=pio_id)
        customer = pio.customer

    if request.method == 'POST':
        print("Raw POST data:", request.POST) 
        if 'create_pio' in request.POST:  
            pio_form = PioForm(request.POST)
            print("Form Data Received:", pio_form.data)
            if pio_form.is_valid():
                pio = pio_form.save()
                return redirect('sale_create_with_pio', pio_id=pio.id)
        else:
            form = SaleForm(request.POST)
            formset = SaleItemFormSet(request.POST)

            print("Formset Errors:", formset.errors)  # Log formset errors

            if form.is_valid() and formset.is_valid():
                customer = form.cleaned_data.get('customer')
                pio = pio or form.cleaned_data.get('pio_number')

                if customer and pio:
                    try:
                        with transaction.atomic():
                            sale = form.save(commit=False)
                            sale.pio_number = pio
                            sale.save()

                            total_sell_price = 0
                            total_profit = 0

                            # Create a list of products to update stock after the sale
                            product_updates = {}

                            # Loop through each form in the formset
                            for item_form in formset:
                                if item_form.is_valid() and item_form.cleaned_data:
                                    product = item_form.cleaned_data['product']
                                    quantity = item_form.cleaned_data['quantity']
                                    sell_price = item_form.cleaned_data['sell_price']

                                    # Check if enough stock is available before proceeding
                                    if product.stock < quantity:
                                        quantity = 0  # Ensure stock is not overdrawn

                                    item_total = quantity * sell_price
                                    profit_per_item = sell_price - product.purchase_price
                                    item_profit = quantity * profit_per_item

                                    total_sell_price += item_total
                                    total_profit += item_profit

                                    SaleItem.objects.create(
                                        sale=sale,
                                        product=product,
                                        quantity=quantity,
                                        sell_price=sell_price,
                                        total_price=item_total,
                                        profit_per_item=profit_per_item,
                                        total_profit=item_profit
                                    )

                                    # Store stock update for later
                                    if product in product_updates:
                                        product_updates[product] += quantity
                                    else:
                                        product_updates[product] = quantity

                            # Update product stock after all sale items are processed
                            for product, quantity in product_updates.items():
                                if product.stock >= quantity:
                                    product.stock -= quantity
                                    product.save(update_fields=['stock'])

                            sale.total_sell_price = total_sell_price
                            sale.total_profit = total_profit
                            sale.save()

                            pio.total_amount = total_sell_price
                            if customer.category == 'buyer':
                                pio.buyer_due = total_sell_price
                            else:
                                pio.seller_due = total_sell_price
                            pio.save(update_fields=['total_amount', 'buyer_due', 'seller_due'])

                            customer.total_due = sum(s.total_sell_price for s in customer.sales.all())
                            customer.save(update_fields=['total_due'])

                        return redirect('sale_list')

                    except Exception as e:
                        return JsonResponse({'error': str(e)}, status=400)

            return JsonResponse({'error': 'Invalid form data', 'form_errors': form.errors, 'formset_errors': formset.errors}, status=400)

    else:
        pio_form = PioForm()
        form = SaleForm(initial={'customer': customer, 'pio_number': pio})
        formset = SaleItemFormSet(queryset=SaleItem.objects.none())

    return render(request, 'sellApp/sale_form.html', {
        'pio_form': pio_form,
        'form': form,
        'formset': formset,
        'pio': pio,
    })
