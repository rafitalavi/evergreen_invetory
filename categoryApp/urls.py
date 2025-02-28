from django.urls import path
from .views import category_list, category_create, category_update, category_delete

urlpatterns = [
    path('category/', category_list, name='category_list'),  # List all categories
    path('category/create/', category_create, name='category_create'),  # Create category
    path('category/update/<int:pk>/', category_update, name='category_update'),  # Update category
    path('category/delete/<int:pk>/', category_delete, name='category_delete'),  # Delete category
]
