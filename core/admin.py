# core/admin.py
from django.contrib import admin
from .models import Dish, Order, OrderItem, Category, Company

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']
    search_fields = ['name']
    list_filter = ['price', 'category']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'delivery_date', 'delivery_time', 'delivery_address', 'status']
    list_filter = ['status', 'delivery_date', 'company']
    search_fields = ['company__name', 'id']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'dish', 'quantity']
    list_filter = ['order__id', 'dish__name']