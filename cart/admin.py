from django.contrib import admin

from .models import Cart, CartItem


class CartItemsInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemsInline, ]
