from django.urls import path
from .views import (
    CartView, AddToCartView, UpdateCartItemView, RemoveFromCartView,
    DeliveryAddressListCreateView, DeliveryAddressDeleteView,
    OrderCreateView, OrderListView, OrderDetailView,
    OrderListForStaffView, OrderStatusUpdateByStaffView,
)

urlpatterns = [

    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='cart-add'),
    path('cart/update/<int:pk>/', UpdateCartItemView.as_view(), name='cart-update'),
    path('cart/remove/<int:pk>/', RemoveFromCartView.as_view(), name='cart-remove'),



    path('addresses/', DeliveryAddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', DeliveryAddressDeleteView.as_view(), name='address-delete'),


    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),


    path('staff/orders/', OrderListForStaffView.as_view(), name='staff-order-list'),
    path('staff/orders/<int:pk>/status/', OrderStatusUpdateByStaffView.as_view(), name='staff-order-status-update'),
]
