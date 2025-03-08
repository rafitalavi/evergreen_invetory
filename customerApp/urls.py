from django.urls import path
from . import views

urlpatterns = [
    path('customers/', views.customer_list, name='customer_list'),
    path('customer/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customer/create/', views.customer_create, name='customer_create'),  # Create customer path
    path('customer/edit/<int:pk>/', views.customer_edit, name='customer_edit'),  # Edit customer path
    path('customer/delete/<int:pk>/', views.customer_delete, name='customer_delete'),
    path('customer/<int:customer_id>/create_transaction/<int:pio_id>/', views.create_transaction, name='create_transaction'),
    path('customer/pio/<int:pio_id>/', views.pio_details, name='pio_details'),

]
