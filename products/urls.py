from django.urls import path
from .views import CategoryListView, ProductListView, ProductDetailView, StaffImportView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('staff/import/', StaffImportView.as_view(), name='staff-import'),
]
