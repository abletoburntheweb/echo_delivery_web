# api/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from core.models import Category, Dish, Company, Ordr, OrdrItem
from .serializers import *
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    try:
        print('📨 Получены данные регистрации:', request.data)

        serializer = UserRegistrationSerializer(data=request.data)
        print('🔍 Сериализатор создан')

        if serializer.is_valid():
            print('✅ Данные валидны')

            if User.objects.filter(email=serializer.validated_data['email']).exists():
                print('❌ Пользователь с таким email уже существует')
                return Response(
                    {'error': 'Пользователь с таким email уже существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(username=serializer.validated_data['username']).exists():
                print('❌ Пользователь с таким именем уже существует')
                return Response(
                    {'error': 'Пользователь с таким именем уже существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            print('🚀 Создаем пользователя...')
            user = serializer.save()
            print(f'✅ Пользователь создан: {user.username}, {user.email}')

            return Response({
                'message': 'Регистрация успешна',
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        else:
            print('❌ Ошибки валидации:', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print('🔴 Ошибка сервера:', str(e))
        import traceback
        print('🔴 Traceback:', traceback.format_exc())
        return Response(
            {'error': f'Ошибка сервера: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    try:
        print('🔐 Получены данные входа:', request.data)

        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            print(f'🔍 Ищем пользователя: {email}')

            try:
                user = User.objects.get(email=email)
                print(f'✅ Пользователь найден: {user.username}')

                user = authenticate(username=user.username, password=password)
                print(f'🔐 Результат аутентификации: {user is not None}')

                if user:
                    from core.models import Company
                    try:
                        company = Company.objects.get(email=email)
                        print(f'🏢 Компания найдена: {company.name}')
                        return Response({
                            'message': 'Вход успешен',
                            'user_id': user.id,
                            'company_id': company.id_company,
                            'company_name': company.name,
                            'email': user.email,
                            'phone': company.phone,
                            'address': company.address
                        })
                    except Company.DoesNotExist:
                        print('⚠️ Компания не найдена')
                        return Response({
                            'message': 'Вход успешен (компания не найдена)',
                            'user_id': user.id,
                            'email': user.email
                        })
                else:
                    print('❌ Неверный пароль')
                    return Response(
                        {'error': 'Неверный пароль'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            except User.DoesNotExist:
                print('❌ Пользователь не найден')
                return Response(
                    {'error': 'Пользователь не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )

        print('❌ Ошибки валидации:', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print('🔴 Ошибка сервера при входе:', str(e))
        import traceback
        print('🔴 Traceback:', traceback.format_exc())
        return Response(
            {'error': f'Ошибка сервера: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_user_orders(request):
    try:
        print('📨 Получен запрос на заказы:', request.GET)

        email = request.GET.get('email')
        if not email:
            print('❌ Email не передан в параметрах')
            return Response(
                {'error': 'Email parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f'🔍 Ищем компанию по email: {email}')

        company = Company.objects.get(email=email)
        orders = Ordr.objects.filter(id_company=company)

        order_dates = [
            order.delivery_date.strftime('%Y-%m-%d')
            for order in orders
            if order.delivery_date
        ]

        print(f'✅ Найдено заказов: {len(order_dates)}')

        return Response({
            'order_dates': order_dates,
            'company_id': company.id_company
        })

    except Company.DoesNotExist:
        print(f'❌ Компания с email {email} не найдена')
        return Response(
            {'error': 'Компания не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f'🔴 Ошибка сервера: {str(e)}')
        import traceback
        print(f'🔴 Traceback: {traceback.format_exc()}')
        return Response(
            {'error': f'Ошибка сервера: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_order(request):
    try:
        print('📦 Создание заказа из Flutter:', request.data)

        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        company = Company.objects.get(email=email)

        order_data = request.data
        order = Ordr.objects.create(
            id_company=company,
            delivery_date=order_data.get('delivery_date'),
            delivery_time=order_data.get('delivery_time'),
            delivery_address=order_data.get('delivery_address'),
            status='новый'
        )

        items = order_data.get('items', [])
        for item in items:
            dish = Dish.objects.get(id_dish=item['dish_id'])
            OrdrItem.objects.create(
                id_ordr=order,
                id_dish=dish,
                quantity=item['quantity']
            )

        print(f'✅ Заказ создан: ID {order.id_order}')

        return Response({
            'message': 'Заказ успешно создан',
            'order_id': order.id_order,
            'delivery_date': order.delivery_date
        }, status=status.HTTP_201_CREATED)

    except Company.DoesNotExist:
        return Response(
            {'error': 'Компания не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Dish.DoesNotExist:
        return Response(
            {'error': 'Блюдо не найдено'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print('🔴 Ошибка создания заказа:', str(e))
        return Response(
            {'error': f'Ошибка сервера: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_site_status(request):
    try:
        from core.views import get_work_dates, get_admin_setting

        work_dates = get_work_dates()
        block_enabled = get_admin_setting('block_enabled', False)

        return Response({
            'site_blocked': block_enabled,
            'maintenance_mode': work_dates['enabled'],
            'maintenance_text': work_dates['display_text']
        })

    except Exception as e:
        print(f'🔴 Ошибка получения статуса сайта: {e}')
        return Response({
            'site_blocked': False,
            'maintenance_mode': False,
            'maintenance_text': ''
        })

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_id = request.query_params.get('category_id')
        if category_id:
            dishes = Dish.objects.filter(id_category_id=category_id)
            serializer = self.get_serializer(dishes, many=True)
            return Response(serializer.data)
        return Response([])


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Ordr.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        orders = Ordr.objects.filter(id_company__email=request.user.email)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

