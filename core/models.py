# core/models.py
from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_company')
    name = models.CharField(max_length=255, verbose_name="Название", db_column='name')
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True, null=True, db_column='phone')
    email = models.EmailField(verbose_name="Email", blank=True, null=True, db_column='email')
    address = models.TextField(verbose_name="Адрес", blank=True, null=True, db_column='address')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Контора"
        verbose_name_plural = "Конторы"
        db_table = 'Контора'
        managed = False

class Category(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_cat')
    name = models.CharField(max_length=255, verbose_name="Название категории", unique=True, db_column='name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        db_table = 'Категория'
        managed = False

class Dish(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_blu')
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, db_column='fk_id_cat', verbose_name="Категория")
    name = models.CharField(max_length=255, verbose_name="Название", db_column='name')
    description = models.TextField(verbose_name="Описание", blank=True, null=True, db_column='description')
    image = models.URLField(verbose_name="Изображение", db_column='img')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена", default=0.00, db_column='price')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        db_table = 'Блюдо'
        managed = False

class Order(models.Model):
    STATUS_CHOICES = [
        ('новый', 'Новый'),
        ('в_работе', 'В работе'),
        ('готов', 'Готов'),
        ('доставлен', 'Доставлен'),
        ('отменен', 'Отменен'),
    ]
    id = models.AutoField(primary_key=True, db_column='id_order')
    company = models.ForeignKey(Company, on_delete=models.RESTRICT, db_column='fk_id_company', verbose_name="Контора")
    delivery_date = models.DateField(verbose_name="Дата доставки", db_column='deliverydate')
    delivery_time = models.TimeField(verbose_name="Время доставки", blank=True, null=True, db_column='deliverytime')
    delivery_address = models.TextField(verbose_name="Адрес доставки", db_column='deliveryaddress')
    status = models.CharField(max_length=20, verbose_name="Статус", choices=STATUS_CHOICES, default='новый', db_column='status')

    def __str__(self):
        return f"Заказ {self.id} от {self.company.name}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        db_table = 'Заказ'
        managed = False

class OrderItem(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_item')
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, db_column='fk_id_order', verbose_name="Заказ")
    dish = models.ForeignKey(Dish, on_delete=models.RESTRICT, db_column='fk_id_blu', verbose_name="Блюдо")
    quantity = models.PositiveIntegerField(verbose_name="Количество", db_column='quantity')

    def __str__(self):
        return f"{self.quantity} x {self.dish.name}"

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"
        db_table = 'СоставЗаказа'
        managed = False