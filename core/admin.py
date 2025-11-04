# core/admin.py
from django.contrib import admin
from .models import Dish, Order, OrderItem, Category, Company # Импортируем Company, если нужно в OrderAdmin

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']  # Добавим category для удобства
    search_fields = ['name']
    list_filter = ['price', 'category'] # Добавим фильтр по категории

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Заменяем старые поля на новые из модели Order
    list_display = ['id', 'company', 'delivery_date', 'delivery_time', 'delivery_address', 'status']
    list_filter = ['status', 'delivery_date', 'company'] # Заменяем фильтры
    search_fields = ['company__name', 'id'] # Ищем по имени компании, а не по юзернейму пользователя

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'dish', 'quantity']
    # Можно добавить фильтры по заказу или блюду, если нужно
    list_filter = ['order__id', 'dish__name'] # Пример фильтрации по связанным полям