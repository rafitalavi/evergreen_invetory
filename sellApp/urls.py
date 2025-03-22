from django.urls import path
from .views import sale_list ,sale_detail , sale_create ,sale_update ,sale_delete

urlpatterns = [
    path('', sale_list, name='sale_list'),
    path('<uuid:pk>/', sale_detail, name='sale_detail'),
    path('sale_create/', sale_create, name='sale_create'),
    path('sale_create/<int:pio_id>/', sale_create, name='sale_create_with_pio'),
path('sales/update/<uuid:pk>/', sale_update, name='sale_update'),
    path('<uuid:pk>/', sale_delete, name='sale_delete'),

]
