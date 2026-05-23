from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Shop

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('user_type',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('user_type',)}),
    )

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_open')
