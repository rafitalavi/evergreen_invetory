from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import ProductForm

# List All Products
from django.shortcuts import render
from .models import Product

def product_list(request):
    query = request.GET.get('q', '')  # Get the search term
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)  # Case-insensitive search

    return render(request, 'productsApp/product_list.html', {'products': products})

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
