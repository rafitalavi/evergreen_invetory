from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_expense, name='create_expense'),
    path('edit/<uuid:pk>/', views.edit_expense, name='expense_edit'),
    path('delete/<uuid:pk>/', views.delete_expense, name='expense_delete'),
    # Include other URLs, such as the expense list page
    path('', views.expense_list_and_profit_summary, name='expense_list'),
]
