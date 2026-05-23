from rest_framework.permissions import BasePermission

class IsSupplierForOrder(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.user.user_type == 'supplier':
            shop = getattr(request.user, 'shop', None)
            if shop is None:
                return False
            return obj.items.filter(product_info__shop=shop).exists()
        return False
