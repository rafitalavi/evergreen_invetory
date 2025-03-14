from django.urls import path
from .views import (
    purchase_list, purchase_create, purchase_update, purchase_delete,
    purchase_detail, purchase_item_create, purchase_item_update, purchase_item_delete
)

urlpatterns = [
    path('', purchase_list, name='purchase_list'),
    path('create/', purchase_create, name='purchase_create'),  # Route without pio_id
    path('create/<int:pio_id>/', purchase_create, name='purchase_create_with_pio'),  # Route with pio_id
    path('<uuid:pk>/', purchase_detail, name='purchase_detail'),
    path('<uuid:pk>/update/', purchase_update, name='purchase_update'),
    path('<uuid:pk>/delete/', purchase_delete, name='purchase_delete'),

    # Purchase Item URLs
    path('<uuid:purchase_id>/item/create/', purchase_item_create, name='purchase_item_create'),
    path('item/<int:pk>/update/', purchase_item_update, name='purchase_item_update'),
    path('item/<int:pk>/delete/', purchase_item_delete, name='purchase_item_delete'),
]
