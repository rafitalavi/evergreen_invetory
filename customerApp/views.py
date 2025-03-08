from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator

from .forms import CustomerForm, TransactionForm
from django.db.models import Q
from datetime import datetime
from .models import Customer, Pio ,Transaction, PaymentRecord

# Customer List View
def customer_list(request):
    # Get search query and filter by category and date range
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Filtering customers based on the search, category, and date range
    customers = Customer.objects.all()

    if search_query:
        customers = customers.filter(name__icontains=search_query)

    if category_filter:
        customers = customers.filter(category=category_filter)

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        customers = customers.filter(updated_at__range=[start_date, end_date])

    # Pagination
    paginator = Paginator(customers, 10)  # 10 customers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customerApp/customer_list.html', {
        'customers': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'start_date': start_date,
        'end_date': end_date
    })


# Customer Detail View
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    # Get filter parameters for PIO list (same as in the customer list)
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    pio_number = request.GET.get('pio_number', '')
    # Filter Purchase Order Items (PIO List) based on customer type (Buyer/Seller)
    if customer.category == 'buyer':
        pio_list = Pio.objects.filter(customer=customer)
    elif customer.category == 'seller':
        pio_list = Pio.objects.filter(customer=customer)

    # Apply date filters if provided
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        pio_list = pio_list.filter(created_at__range=[start_date, end_date])
    if pio_number:
        pio_list = pio_list.filter(pio_number__icontains=pio_number)
    # Pagination for PIO List (10 items per page)
    paginator = Paginator(pio_list, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate buyer or seller due
    buyer_due = customer.total_due - customer.total_paid if customer.category == 'buyer' else None
    seller_due = customer.total_due - customer.total_paid if customer.category == 'seller' else None

    return render(request, 'customerApp/customer_detail.html', {
        'customer': customer,
        'page_obj': page_obj,
        'start_date': start_date,
        'end_date': end_date,
        'buyer_due': buyer_due,
        'seller_due': seller_due,
        'pio_number': pio_number
    })


# Customer Create View
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')  # Redirect to the customer list page
    else:
        form = CustomerForm()

    return render(request, 'customerApp/customer_create.html', {'form': form})


# Customer Edit View
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'customerApp/customer_edit.html', {'form': form, 'customer': customer})


# Customer Delete View
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('customer_list')


# Add transaction (if necessary)
def create_transaction(request, customer_id, pio_id):
    # Fetch customer and PIO objects using their ids
    customer = get_object_or_404(Customer, id=customer_id)
    pio = get_object_or_404(Pio, id=pio_id)

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        print("Form Data:", request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.customer = customer
            transaction.pio = pio
            transaction.save()
            # Redirect to the customer detail or transaction list page
            return redirect('customer_detail', pk=customer.id)
        else:
            # Handle form errors
            print(form.errors)  # For debugging; remove or handle errors properly in the template
    else:
        form = TransactionForm()

    return render(request, 'customerApp/create_transaction.html', {'form': form, 'customer': customer, 'pio': pio})# Edit transaction (if necessary)
def edit_transaction(request, pk):
    # Implement logic to edit transaction
    pass


# Delete transaction (if necessary)
def delete_transaction(request, pk):
    # Implement logic to delete transaction
    pass
#pio details page
def pio_details(request, pio_id):
    pio = get_object_or_404(Pio, id=pio_id)
    transactions = pio.transactions.all()  # Fetch all transactions linked to this PIO

    return render(request, 'customerApp/pio_details.html', {'pio': pio, 'transactions': transactions})
