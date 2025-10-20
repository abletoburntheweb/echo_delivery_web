# core/admin.py
from django.contrib import admin
from .models import Dish, Order, OrderItem

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']  # Какие поля показывать в списке
    search_fields = ['name']          # По каким полям можно искать
    list_filter = ['price']           # Фильтры по цене

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'date', 'total', 'created_at']
    list_filter = ['date', 'user', 'created_at']
    search_fields = ['user__username', 'id']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'dish', 'quantity']
    list_filter = ['order', 'dish']