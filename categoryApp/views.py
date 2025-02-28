from django.shortcuts import render, redirect, get_object_or_404
from .models import Category
from .forms import CategoryForm

# List All Categories
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categoryApp/list.html', {'categories': categories})

# Create a New Category
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')  # ✅ Corrected
    else:
        form = CategoryForm()
    return render(request, 'categoryApp/form.html', {'form': form})

# Update an Existing Category
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')  # ✅ Corrected
    else:
        form = CategoryForm(instance=category)
    return render(request, 'categoryApp/form.html', {'form': form})

# Delete a Category
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        return redirect('category_list')  # ✅ Corrected
    return render(request, 'categoryApp/confirm_delete.html', {'category': category})
