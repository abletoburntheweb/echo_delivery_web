# core/models.py
from django.db import models
from django.contrib.auth.models import User # Импортируем встроенный User

# --- Таблица Контора (Company) ---
class Company(models.Model):
    # id Django автоматически создаст, но наша таблица использует ID_COMPANY как первичный ключ
    # Поэтому мы переопределим поле id
    # ВАЖНО: db_column должен быть в нижнем регистре, как его сохранила PostgreSQL
    id = models.AutoField(primary_key=True, db_column='id_company') # <-- Изменено с 'ID_COMPANY'
    name = models.CharField(max_length=255, verbose_name="Название", db_column='name') # <-- Изменено с 'Name'
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True, null=True, db_column='phone') # <-- Изменено с 'Phone'
    email = models.EmailField(verbose_name="Email", blank=True, null=True, db_column='email') # <-- Изменено с 'Email'
    # Не рекомендуется хранить PasswordHash напрямую, Django хэширует пароли через User
    # Если ты хочешь хранить его, добавь: password_hash = models.CharField(max_length=255, db_column='passwordhash') # <-- Если был без кавычек
    address = models.TextField(verbose_name="Адрес", blank=True, null=True, db_column='address') # <-- Изменено с 'Address'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Контора"
        verbose_name_plural = "Конторы"
        db_table = 'Контора' # Точное имя таблицы в БД
        managed = False # Django не управляет этой таблицей

# --- Таблица Категория (Category) ---
class Category(models.Model):
    # id Django автоматически создаст, но наша таблица использует ID_CAT как первичный ключ
    # Поэтому мы переопределим поле id
    # ВАЖНО: db_column должен быть в нижнем регистре, как его сохранила PostgreSQL
    id = models.AutoField(primary_key=True, db_column='id_cat') # <-- Изменено с 'ID_CAT'
    name = models.CharField(max_length=255, verbose_name="Название категории", unique=True, db_column='name') # <-- Изменено с 'Name'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        db_table = 'Категория' # Точное имя таблицы в БД
        managed = False # Django не управляет этой таблицей

# --- Таблица Блюдо (Dish) ---
class Dish(models.Model):
    # id Django автоматически создаст, но наша таблица использует ID_BLU как первичный ключ
    # ВАЖНО: db_column должен быть в нижнем регистре, как его сохранила PostgreSQL
    id = models.AutoField(primary_key=True, db_column='id_blu') # <-- Изменено с 'ID_BLU'
    # FK_ID_CAT -> Связь с Category
    # ВАЖНО: db_column должен быть в нижнем регистре, как его сохранила PostgreSQL
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, db_column='fk_id_cat', verbose_name="Категория")
    name = models.CharField(max_length=255, verbose_name="Название", db_column='name') # <-- Изменено с 'Name'
    # DESCRIPTION -> description
    description = models.TextField(verbose_name="Описание", blank=True, null=True, db_column='description') # <-- Изменено с 'DESCRIPTION'
    # IMG -> image
    image = models.URLField(verbose_name="Изображение", db_column='img') # <-- Изменено с 'IMG'
    # Price -> price
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена", default=0.00, db_column='price') # <-- Изменено с 'Price'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        db_table = 'Блюдо' # Точное имя таблицы в БД
        managed = False # Django не управляет этой таблицей

# --- Таблица Заказ (Order) ---
class Order(models.Model):
    STATUS_CHOICES = [
        ('новый', 'Новый'),
        ('в_работе', 'В работе'),
        ('готов', 'Готов'),
        ('доставлен', 'Доставлен'),
        ('отменен', 'Отменен'),
    ]
    # id Django автоматически создаст, но наша таблица использует ID_ORDER как первичный ключ
    # ВАЖНО: db_column должен быть в нижнем регистре, как его сохранила PostgreSQL
    id = models.AutoField(primary_key=True, db_column='id_order') # <-- Изменено с 'ID_ORDER'
    # FK_ID_COMPANY -> Связь с Company
    company = models.ForeignKey(Company, on_delete=models.RESTRICT, db_column='fk_id_company', verbose_name="Контора") # <-- Изменено с 'FK_ID_COMPANY'
    # DeliveryDate -> delivery_date
    delivery_date = models.DateField(verbose_name="Дата доставки", db_column='deliverydate') # <-- Изменено с 'DeliveryDate'
    # DeliveryTime -> delivery_time
    delivery_time = models.TimeField(verbose_name="Время доставки", blank=True, null=True, db_column='deliverytime') # <-- Изменено с 'DeliveryTime'
    # DeliveryAddress -> delivery_address
    delivery_address = models.TextField(verbose_name="Адрес доставки", db_column='deliveryaddress') # <-- Изменено с 'DeliveryAddress'
    # Status -> status
    status = models.CharField(max_length=20, verbose_name="Статус", choices=STATUS_CHOICES, default='новый', db_column='status') # <-- Изменено с 'Status'

    def __str__(self):
        return f"Заказ {self.id} от {self.company.name}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        db_table = 'Заказ' # Точное имя таблицы в БД
        managed = False # Django не управляет этой таблицей

# --- Таблица СоставЗаказа (OrderItem) ---
class OrderItem(models.Model):
    # id Django автоматически создаст, но наша таблица использует ID_ITEM как первичный ключ
    # ВАЖНО: db_column должен быть в нижнем регистре, как его сохранила PostgreSQL
    id = models.AutoField(primary_key=True, db_column='id_item') # <-- Изменено с 'ID_ITEM'
    # FK_ID_ORDER -> Связь с Order
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, db_column='fk_id_order', verbose_name="Заказ") # <-- Изменено с 'FK_ID_ORDER'
    # FK_ID_BLU -> Связь с Dish
    dish = models.ForeignKey(Dish, on_delete=models.RESTRICT, db_column='fk_id_blu', verbose_name="Блюдо") # <-- Изменено с 'FK_ID_BLU'
    # Quantity -> quantity
    quantity = models.PositiveIntegerField(verbose_name="Количество", db_column='quantity') # <-- Изменено с 'Quantity'

    def __str__(self):
        return f"{self.quantity} x {self.dish.name}"

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"
        db_table = 'СоставЗаказа' # Точное имя таблицы в БД
        managed = False # Django не управляет этой таблицей