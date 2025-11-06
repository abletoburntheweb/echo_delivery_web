# core/admin.py
from django.contrib import admin
from .models import Dish, Ordr, OrdrItem, Category, Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id_company', 'name', 'phone', 'email', 'address')
    search_fields = ('name', 'phone', 'email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id_category', 'name')
    search_fields = ('name',)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('id_dish', 'name', 'id_category', 'price')
    list_filter = ('id_category',)
    search_fields = ('name', 'description')


@admin.register(Ordr)
class OrdrAdmin(admin.ModelAdmin):
    list_display = ('id_ordr', 'id_company', 'delivery_date', 'delivery_time', 'delivery_address', 'status')
    list_filter = ('delivery_date', 'id_company', 'status')
    search_fields = ('delivery_address', 'id_company__name')


@admin.register(OrdrItem)
class OrdrItemAdmin(admin.ModelAdmin):
    list_display = ('id_ordritem', 'id_ordr', 'id_dish', 'quantity')
    list_filter = ('id_ordr__delivery_date', 'id_dish__name')
    search_fields = ('id_ordr__id_ordr', 'id_dish__name')