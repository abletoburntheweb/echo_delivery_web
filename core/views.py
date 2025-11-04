from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404 # Импортируем get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.urls import reverse
from datetime import datetime, timedelta
from .models import Dish, Category # Импортируем модели

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_calendar')
        else:
            return redirect('calendar')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_calendar')
            else:
                return redirect('calendar')
        else:
            error_message = "Неверный логин или пароль"
            return render(request, 'login.html', {'error_message': error_message})

    else:
        return render(request, 'login.html', {'error_message': None})

def register_view(request):
    if request.method == 'POST':
        return redirect('login')
    else:
        return render(request, 'register.html')

@login_required
def calendar_view(request):
    today = datetime.now().date()
    days = []
    for i in range(14):
        day = today + timedelta(days=i)
        days.append({
            'date': day,
            'weekday': day.weekday(),
            'is_today': day == today
        })

    month_name = today.strftime('%B')
    selected_date_str = None

    if request.method == 'POST':
        selected_date_str = request.POST.get('selected_date')
        if selected_date_str:
            try:
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
                print(f"Дата выбрана: {selected_date}")
                request.session['selected_date'] = selected_date_str
                # <-- ВАЖНО: Редирект в cart_view
                return redirect('cart')  # <-- cart_view сам определит, какой шаблон использовать (cart или admin_cart)
            except ValueError:
                print("Неверный формат даты")
                pass

    selected_date_str = request.session.get('selected_date')
    selected_date = None
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    return render(request, 'calendar.html', {
        'days': days,
        'month_name': month_name,
        'selected_date': selected_date
    })

@user_passes_test(lambda u: u.is_superuser)
def admin_calendar_view(request):
    today = datetime.now().date()
    days = []
    for i in range(14):
        day = today + timedelta(days=i)
        days.append({
            'date': day,
            'weekday': day.weekday(),
            'is_today': day == today
        })

    month_name = today.strftime('%B')
    selected_date_str = None

    if request.method == 'POST':
        selected_date_str = request.POST.get('selected_date')
        if selected_date_str:
            try:
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
                print(f"Дата выбрана (админ): {selected_date}")
                request.session['selected_date'] = selected_date_str
                # --- Добавляем редирект ---
                return redirect('cart') # или redirect('admin_cart')
                # ------------------------
            except ValueError:
                print("Неверный формат даты")
                pass

    selected_date_str = request.session.get('selected_date')
    selected_date = None
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    return render(request, 'admin_calendar.html', {
        'days': days,
        'month_name': month_name,
        'selected_date': selected_date
    })

@login_required
def cart_view(request):
    selected_date_str = request.session.get('selected_date')
    if not selected_date_str:
        return redirect('calendar')

    all_carts = request.session.get('carts', {})
    cart_items = all_carts.get(selected_date_str, [])

    total = sum(item['quantity'] * item['price'] for item in cart_items)
    if not cart_items:
        cart_items = None

    if request.user.is_superuser:
        template_name = 'admin_cart.html'
    else:
        template_name = 'cart.html'

    return render(request, template_name, {
        'cart_items': cart_items,
        'total': total,
        'item_count': len(cart_items) if cart_items else 0
    })

@login_required
def update_cart(request):
    if request.method == 'POST':
        selected_date_str = request.session.get('selected_date')
        if not selected_date_str:
            return redirect('calendar')

        dish_id = request.POST.get('dish_id')
        quantity = request.POST.get('quantity')
        remove = request.POST.get('remove')

        all_carts = request.session.get('carts', {})
        cart = all_carts.get(selected_date_str, [])

        if remove == 'true' or (quantity and int(quantity) <= 0):
            cart = [item for item in cart if item['id'] != dish_id]
        elif quantity:
            found = False
            for item in cart:
                if item['id'] == dish_id:
                    item['quantity'] = int(quantity)
                    found = True
                    break

        all_carts[selected_date_str] = cart
        request.session['carts'] = all_carts

    referer = request.META.get('HTTP_REFERER', '')
    if 'admin/cart' in referer:
        return redirect('admin_cart')
    else:
        return redirect('cart')


@login_required
def menu_view(request):
    # Убираем "виртуальный" список
    # dishes = [ ... ]
    # Получаем блюда из базы данных
    dishes = Dish.objects.select_related('category').all()
    return render(request, 'menu.html', {'dishes': dishes})

# Убираем функцию _get_dish_by_id
# def _get_dish_by_id(dish_id):
#     # ...
#     return ...

@login_required
def dish_detail_view(request, dish_id):
    print(f"Запрошенное dish_id: {dish_id}")
    # Убираем вызов _get_dish_by_id
    # dish = _get_dish_by_id(dish_id)

    # Получаем блюдо из базы данных
    dish = get_object_or_404(Dish, id=dish_id) # Используем get_object_or_404 для краткости
    print(f"Найдено блюдо из базы: {dish}")
    # Передаём объект dish в шаблон
    return render(request, 'dish_detail.html', {'dish': dish})

@user_passes_test(lambda u: u.is_superuser)
def admin_dish_detail_view(request, dish_id):
    print(f"admin_dish_detail_view вызвана для dish_id: {dish_id}")
    # Убираем вызов _get_dish_by_id
    # dish = _get_dish_by_id(dish_id)

    # Получаем блюдо из базы данных
    dish = get_object_or_404(Dish, id=dish_id) # Используем get_object_or_404 для краткости
    # previous_url = request.META.get('HTTP_REFERER', '')

    # if not previous_url or not previous_url.startswith('/admin/'):
    #     previous_url = reverse('admin_menu')

    # print(f"Рендерим admin_dish_detail.html. Предыдущая страница: {previous_url}")

    return render(request, 'admin_dish_detail.html', {
        'dish': dish,
        # 'previous_url': previous_url # Убрано, если не нужно
    })

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        selected_date_str = request.session.get('selected_date')
        if not selected_date_str:
            return redirect('calendar')

        dish_id = request.POST.get('dish_id')
        # dish_name = request.POST.get('dish_name') # Убираем, получаем из базы
        # dish_price = request.POST.get('dish_price') # Убираем, получаем из базы
        # dish_image = request.POST.get('dish_image') # Убираем, получаем из базы
        quantity = int(request.POST.get('quantity', 1))

        # Получаем блюдо из базы, чтобы получить его данные
        try:
            dish_obj = Dish.objects.get(id=dish_id)
        except Dish.DoesNotExist:
            print(f"Блюдо с ID {dish_id} не найдено в базе данных при добавлении в корзину")
            return redirect('menu') # Или возвращаем ошибку

        all_carts = request.session.get('carts', {})
        cart = all_carts.get(selected_date_str, [])

        found = False
        for item in cart:
            if item['id'] == dish_id:
                item['quantity'] += quantity
                found = True
                break

        if not found:
            # Используем данные из объекта модели Dish
            cart.append({
                'id': dish_obj.id,
                'name': dish_obj.name,
                'price': float(dish_obj.price),
                'image': dish_obj.image,
                'quantity': quantity
            })

        all_carts[selected_date_str] = cart
        request.session['carts'] = all_carts

        return redirect('menu')

    return redirect('menu')

@login_required
def receipt_view(request):
    selected_date_str = request.session.get('selected_date')
    if not selected_date_str:
        return redirect('calendar')

    all_carts = request.session.get('carts', {})
    cart_items = all_carts.get(selected_date_str, [])

    total = 0
    for item in cart_items:
        item_total = item['price'] * item['quantity']
        item['total_price'] = item_total
        total += item_total

    selected_date = None
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if not cart_items:
        return redirect('cart')

    return render(request, 'receipt.html', {
        'cart_items': cart_items,
        'total': total,
        'selected_date': selected_date
    })

@login_required
def faq_view(request):
    return render(request, 'faq.html')

@login_required
def profile_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

    if request.user.is_superuser:
        template_name = 'admin_profile.html'
    else:
        template_name = 'profile.html'

    return render(request, template_name, {'user': request.user})

@login_required
def agreement_view(request):
    return render(request, 'agreement.html')

@user_passes_test(lambda u: u.is_superuser)
@login_required
def admin_menu_view(request):
    categories = Category.objects.all()
    dishes = Dish.objects.select_related('category').all()
    # Передаём и категории, и блюда в шаблон
    return render(request, 'admin_menu.html', {'dishes': dishes, 'categories': categories})

@login_required
@user_passes_test(lambda u: u.is_superuser) # Только администратор может редактировать
def update_dish(request, dish_id): # Принимаем dish_id из URL
    if request.method == 'POST':
        try:
            # Найти блюдо по ID
            dish = get_object_or_404(Dish, id=dish_id)

            # Получить новые данные из POST-запроса
            new_name = request.POST.get('name')
            new_description = request.POST.get('description')
            new_price_str = request.POST.get('price')

            # Валидация (простая)
            errors = []
            if not new_name or new_name.strip() == '':
                errors.append("Имя не может быть пустым.")
            if not new_price_str:
                errors.append("Цена не может быть пустой.")
            else:
                try:
                    new_price = float(new_price_str)
                    if new_price < 0:
                         errors.append("Цена не может быть отрицательной.")
                except ValueError:
                    errors.append("Цена должна быть числом.")

            if errors:
                # Вернуть ошибки как ответ (можно сделать красивее)
                return HttpResponse("; ".join(errors), status=400)

            # Обновить поля блюда
            dish.name = new_name.strip()
            dish.description = new_description # может быть пустым
            dish.price = new_price

            # Сохранить изменения в базу данных
            dish.save()

            # Вернуть успешный ответ
            return HttpResponse("OK", status=200)

        except Exception as e:
            # Обработать возможные ошибки при сохранении
            print(f"Ошибка при обновлении блюда {dish_id}: {e}")
            return HttpResponse("Ошибка сервера при сохранении.", status=500)

    else:
        # Если не POST, вернуть 405 Method Not Allowed
        return HttpResponse("Метод не разрешён.", status=405)