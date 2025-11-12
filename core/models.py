from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    id_company = models.AutoField(primary_key=True, db_column='id_company')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    address = models.TextField()

    class Meta:
        db_table = 'company'
        verbose_name = 'Компания'

    def __str__(self):
        return self.name


class Category(models.Model):
    id_category = models.AutoField(primary_key=True, db_column='id_cat')
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'category'
        verbose_name = 'Категория'
    def __str__(self):
        return self.name


class Dish(models.Model):
    id_dish = models.AutoField(primary_key=True, db_column='id_blu')
    id_category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='fk_id_cat', related_name='dishes')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    img = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'dish'
        verbose_name = 'Блюдо'

    def __str__(self):
        return self.name


class Ordr(models.Model):
    id_order = models.AutoField(primary_key=True)
    id_company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='fk_id_company')
    delivery_date = models.DateField(db_column='deliverydate')
    delivery_time = models.TimeField(blank=True, null=True, db_column='deliverytime')
    delivery_address = models.TextField(db_column='deliveryaddress')
    status = models.CharField(max_length=20, default='новый')

    class Meta:
        db_table = 'ordr'
        verbose_name = 'Заказ'

    def __str__(self):
        return f"Заказ №{self.id_order} от {self.delivery_date}"


class OrdrItem(models.Model):
    id_ordritem = models.AutoField(primary_key=True, db_column='id_item')
    id_ordr = models.ForeignKey(Ordr, on_delete=models.CASCADE, db_column='fk_id_order')
    id_dish = models.ForeignKey(Dish, on_delete=models.CASCADE, db_column='fk_id_blu')
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'ordritem'
        verbose_name = 'Позиции заказов'

    def __str__(self):
        return f"{self.quantity} × {self.id_dish.name} (заказ №{self.id_ordr.id_order})"