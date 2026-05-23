import os
import tempfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, filters, status, permissions
from .models import Product, Category
from .serializers import ProductListSerializer, ProductDetailSerializer, CategorySerializer
from .tasks import do_import

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = []

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.prefetch_related('infos__shop').all()
    serializer_class = ProductListSerializer
    permission_classes = []
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'infos__price']

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.prefetch_related('infos__shop').all()
    serializer_class = ProductDetailSerializer
    permission_classes = []

class StaffImportView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'detail': 'Файл не предоставлен'}, status=status.HTTP_400_BAD_REQUEST)
        uploaded_file = request.FILES['file']
        with tempfile.NamedTemporaryFile(delete=False, suffix='.yaml') as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        do_import.delay(tmp_path)
        return Response({'detail': 'Задача импорта запущена'}, status=status.HTTP_202_ACCEPTED)
