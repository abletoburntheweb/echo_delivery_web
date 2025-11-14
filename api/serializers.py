# api/serializers.py
from rest_framework import serializers
from core.models import Category, Dish, Company, Ordr, OrdrItem
from django.contrib.auth.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    company_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'company_name', 'phone', 'address']

    def create(self, validated_data):
        print('🔍 Создание пользователя с данными:', validated_data)

        company_name = validated_data.pop('company_name', '')
        phone = validated_data.pop('phone', '')
        address = validated_data.pop('address', '')

        print(f'🏢 Создаем компанию: {company_name}, {phone}, {address}')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        print(f'✅ Пользователь создан: {user.id}')

        from core.models import Company
        company = Company.objects.create(
            name=company_name,
            phone=phone,
            email=user.email,
            address=address
        )
        print(f'✅ Компания создана: {company.id_company}')

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id_category', 'name']


class DishSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='id_category.name', read_only=True)

    class Meta:
        model = Dish
        fields = ['id_dish', 'name', 'description', 'price', 'img', 'id_category', 'category_name']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id_company', 'name', 'phone', 'email', 'address']


class OrderItemSerializer(serializers.ModelSerializer):
    dish_name = serializers.CharField(source='id_dish.name', read_only=True)
    dish_price = serializers.DecimalField(source='id_dish.price', read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = OrdrItem
        fields = ['id_ordritem', 'id_dish', 'dish_name', 'dish_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='id_company.name', read_only=True)

    class Meta:
        model = Ordr
        fields = ['id_order', 'id_company', 'company_name', 'delivery_date', 'delivery_time',
                  'delivery_address', 'status', 'items']