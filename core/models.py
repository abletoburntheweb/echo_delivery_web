# core/models.py
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название категории", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Dish(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.URLField(verbose_name="Изображение")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    date = models.DateField(verbose_name="Дата")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итого")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Заказ")
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name="Блюдо")
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    def __str__(self):
        return f"{self.quantity} x {self.dish.name}"

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"
