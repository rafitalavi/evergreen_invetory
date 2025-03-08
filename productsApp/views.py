

from django.shortcuts import render, get_object_or_404, redirect

from .forms import ProductForm

# List All Products


from django.utils.dateparse import parse_date
from .models import Product
from django.db.models import Q
def product_list(request):
    products = Product.objects.all()
    query = request.GET.get('q', '')
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(category__name__icontains=query)
        )

    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        if start_date and end_date:
            products = products.filter(updated_at__date__range=[start_date, end_date])

    context = {
        'products': products,
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'query': query,
    }
    return render(request, 'productsApp/product_list.html', context)


# Create a New Product
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'productsApp/product_form.html', {'form': form})

# Update an Existing Product
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'productsApp/product_form.html', {'form': form})

# Delete a Product
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect('product_list')
    return render(request, 'productsApp/product_confirm_delete.html', {'product': product})
