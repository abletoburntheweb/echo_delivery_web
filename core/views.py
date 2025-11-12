from PIL import Image
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from datetime import datetime, timedelta
from .models import Dish, Category, Company, Ordr, OrdrItem
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import os
from django.conf import settings
from django.core.files.storage import default_storage


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_panel')
        else:
            return redirect('calendar')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_panel')
            else:
                return redirect('calendar')
        else:
            error_message = "Неверный логин или пароль"
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html', {'error_message': None})

def register_view(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Кажется email уже занят.")
            return render(request, 'register.html', {
                'company_name': company_name,
                'address': address,
                'phone': phone,
                'email': email
            })

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password
                )
                company = Company.objects.create(
                    name=company_name,
                    address=address,
                    phone=phone,
                    email=email
                )
                login(request, user)
                return redirect('calendar')
        except Exception as e:
            print(f"[ERROR] Регистрация не удалась: {e}")
            messages.error(request, f"Ошибка при регистрации: {str(e)}")
            return render(request, 'register.html', {
                'company_name': company_name,
                'address': address,
                'phone': phone,
                'email': email
            })
    else:
        return render(request, 'register.html')

@login_required
def calendar_view(request):
    today = datetime.now().date()
    current_monday = today - timedelta(days=today.weekday())
    start_date = current_monday + timedelta(weeks=1)

    days = []
    for i in range(14):
        day = start_date + timedelta(days=i)
        days.append({
            'date': day,
            'weekday': day.weekday(),
            'is_today': day == today
        })

    if request.method == 'POST':
        selected_date_str = request.POST.get('selected_date')
        if selected_date_str:
            try:
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
                print(f"Дата выбрана: {selected_date}")
                request.session['selected_date'] = selected_date_str
                return redirect('cart')
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
        'selected_date': selected_date
    })

@user_passes_test(lambda u: u.is_superuser)
def admin_panel_view(request):
    return render(request, 'admin_panel.html')

@user_passes_test(lambda u: u.is_superuser)
def admin_clients_view(request):
    companies = Company.objects.all().order_by('name')
    return render(request, 'admin_clients.html', {'companies': companies})

@user_passes_test(lambda u: u.is_superuser)
def delete_client_view(request, company_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                company = get_object_or_404(Company, id_company=company_id)
                user = get_object_or_404(User, username=company.email)
                company.delete()
                user.delete()
                messages.success(request, "Клиент успешно удалён.")
        except Exception as e:
            messages.error(request, f"Ошибка при удалении: {str(e)}")
        return redirect('admin_clients')
    return HttpResponse("Метод не разрешён.", status=405)

@user_passes_test(lambda u: u.is_superuser)
def admin_calendar_view(request):
    today = datetime.now().date()
    days = []
    for i in range(21):
        day = today + timedelta(days=i)
        days.append({
            'date': day,
            'weekday': day.weekday(),
            'is_today': day == today
        })

    if request.method == 'POST':
        selected_date_str = request.POST.get('selected_date')
        if selected_date_str:
            try:
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
                request.session['selected_date_admin'] = selected_date_str
                return redirect('admin_orders_by_date')
            except ValueError:
                pass

    return render(request, 'admin_calendar.html', {'days': days})

@user_passes_test(lambda u: u.is_superuser)
def admin_orders_by_date_view(request):
    selected_date_str = request.session.get('selected_date_admin')
    if not selected_date_str:
        return redirect('admin_calendar')

    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        return redirect('admin_calendar')

    orders = Ordr.objects.filter(delivery_date=selected_date).select_related('id_company')

    order_list = []
    for order in orders:
        total_amount = OrdrItem.objects.filter(
            id_ordr=order
        ).aggregate(
            total=Sum(F('quantity') * F('id_dish__price'))
        )['total'] or Decimal('0.00')

        order_list.append({
            'id': order.id_order,
            'company': order.id_company.name,
            'address': order.delivery_address,
            'phone': order.id_company.phone,
            'amount': total_amount,
            'time': order.delivery_time.strftime('%H:%M') if order.delivery_time else '—',
            'status': order.status
        })

    return render(request, 'admin_orders_by_date.html', {
        'orders': order_list,
        'selected_date': selected_date,
        'title': f'Заказы на {selected_date.day} {["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"][selected_date.month - 1]} {selected_date.year} года'
    })

@user_passes_test(lambda u: u.is_superuser)
def admin_delete_order_view(request, order_id):
    if request.method == 'POST':
        try:
            order = get_object_or_404(Ordr, id_ordr=order_id)
            order.delete()
            messages.success(request, "Заказ успешно удалён.")
        except Exception as e:
            messages.error(request, f"Ошибка при удалении: {str(e)}")
        return redirect('admin_orders_by_date')
    return HttpResponse("Метод не разрешён.", status=405)

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
    if request.user.is_superuser:
        return admin_menu_view(request)
    else:
        categories = Category.objects.all()
        dishes = Dish.objects.select_related('id_category').all()
        return render(request, 'menu.html', {'dishes': dishes, 'categories': categories})

@login_required
def dish_detail_view(request, dish_id):
    print(f"Запрошенное dish_id: {dish_id}")
    dish = get_object_or_404(Dish, id_dish=dish_id)
    print(f"Найдено блюдо из базы: {dish}")
    return render(request, 'dish_detail.html', {'dish': dish})

@user_passes_test(lambda u: u.is_superuser)
def admin_dish_detail_view(request, dish_id):
    print(f"admin_dish_detail_view вызвана для dish_id: {dish_id}")
    dish = get_object_or_404(Dish, id_dish=dish_id)
    return render(request, 'admin_dish_detail.html', {
        'dish': dish,
    })


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        selected_date_str = request.session.get('selected_date')
        if not selected_date_str:
            return redirect('calendar')

        dish_id = request.POST.get('dish_id')
        quantity = int(request.POST.get('quantity', 1))

        print(f"DEBUG: dish_id = '{dish_id}', quantity = {quantity}")

        if not dish_id:
            print("ERROR: dish_id is empty!")
            return redirect('menu')

        try:
            dish_obj = Dish.objects.get(id_dish=dish_id)
        except Dish.DoesNotExist:
            print(f"Блюдо с ID {dish_id} не найдено в базе данных при добавлении в корзину")
            return redirect('menu')

        all_carts = request.session.get('carts', {})
        cart = all_carts.get(selected_date_str, [])
        found = False
        for item in cart:
            if item['id'] == dish_id:
                item['quantity'] += quantity
                found = True
                break

        if not found:
            cart.append({
                'id': dish_obj.id_dish,
                'name': dish_obj.name,
                'price': float(dish_obj.price),
                'image': dish_obj.img,
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

    try:
        company = Company.objects.get(email=request.user.email)
    except Company.DoesNotExist:
        company = None

    context = {
        'user': request.user,
        'company': company,
    }

    if request.user.is_superuser:
        template_name = 'admin_profile.html'
    else:
        template_name = 'profile.html'

    return render(request, template_name, context)

@login_required
def agreement_view(request):
    return render(request, 'agreement.html')

@login_required
def admin_logout_view(request):
    logout(request)
    return redirect('login')

@user_passes_test(lambda u: u.is_superuser)
def admin_menu_view(request):
    categories = Category.objects.all()
    dishes = Dish.objects.select_related('id_category').all()
    return render(request, 'admin_menu.html', {'dishes': dishes, 'categories': categories})

@user_passes_test(lambda u: u.is_superuser)
def get_dishes_by_category(request):
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({'success': False, 'error': 'ID категории не передан.'}, status=400)
    try:
        dishes = Dish.objects.filter(id_category_id=category_id).select_related('id_category')
        dish_list = []
        for dish in dishes:
            dish_list.append({
                'id': dish.id_dish,
                'name': dish.name,
                'price': str(dish.price),
                'image': dish.img,
                'category_id': dish.id_category.id_category
            })
        return JsonResponse({'success': True, 'dishes': dish_list})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def update_dish(request, dish_id):
    if request.method == 'POST':
        try:
            dish = get_object_or_404(Dish, id_dish=dish_id)

            new_name = request.POST.get('name', '').strip()
            new_description = request.POST.get('description', '').strip()
            new_price_str = request.POST.get('price')
            new_image_file = request.FILES.get('image')

            errors = []
            if not new_name:
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

            if new_image_file:
                try:
                    img = Image.open(new_image_file)
                    img.verify()
                    new_image_file.seek(0)
                except Exception:
                    errors.append("Новый файл не является изображением.")

            if errors:
                return HttpResponse("; ".join(errors), status=400)

            dish.name = new_name
            dish.description = new_description
            dish.price = new_price

            if new_image_file:
                 print(f"Обновление файла: {new_image_file.name}, размер: {new_image_file.size} байт, тип: {new_image_file.content_type}")
                 try:
                     img = Image.open(new_image_file)
                     print(f"Формат изображения: {img.format}")
                     img.verify()
                     print("Файл прошёл проверку verify().")
                     new_image_file.seek(0)

                     save_path = os.path.join('dishes', new_image_file.name)
                     saved_path = default_storage.save(save_path, new_image_file)
                     dish.img = saved_path

                 except Exception as e:
                     print(f"Ошибка проверки/сохранения нового изображения: {e}")
                     errors.append("Загруженный файл не является изображением или не удалось сохранить.")
                     return HttpResponse("; ".join(errors), status=400)

            dish.save()
            return redirect('admin_menu')

        except Exception as e:
            print(f"Ошибка при обновлении блюда {dish_id}: {e}")
            return HttpResponse("Ошибка сервера при сохранении.", status=500)

    return HttpResponse("Метод не разрешён.", status=405)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_dish_view(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            price_str = request.POST.get('price')
            category_id = request.POST.get('category_id')
            image_file = request.FILES.get('image')

            errors = []
            if not name:
                errors.append("Поле 'Имя' обязательно.")
            if not price_str:
                errors.append("Поле 'Цена' обязательно.")
            if not category_id:
                errors.append("Поле 'Категория' обязательно.")

            price = None
            if price_str:
                try:
                    price = float(price_str)
                    if price < 0:
                        errors.append("Цена не может быть отрицательной.")
                except ValueError:
                    errors.append("Поле 'Цена' должно быть числом.")

            category = None
            if category_id and not errors:
                try:
                    category = Category.objects.get(id_category=category_id)
                except Category.DoesNotExist:
                    errors.append("Выбранная категория не существует.")

            image_path = ""
            if image_file:
                print(f"Загруженный файл: {image_file.name}, размер: {image_file.size} байт, тип: {image_file.content_type}")
                try:
                    img = Image.open(image_file)
                    print(f"Формат изображения: {img.format}")
                    img.verify()
                    print("Файл прошёл проверку verify().")
                    image_file.seek(0)

                    save_path = os.path.join('dishes', image_file.name)

                    saved_path = default_storage.save(save_path, image_file)
                    image_path = saved_path

                except Exception as e:
                    print(f"Ошибка проверки/сохранения изображения: {e}")
                    errors.append("Загруженный файл не является изображением или не удалось сохранить.")

            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=400)

            new_dish = Dish.objects.create(
                name=name,
                description=description,
                price=price,
                id_category=category,
                img=image_path
            )

            return JsonResponse({
                'success': True,
                'message': 'Блюдо успешно добавлено!',
                'dish': {
                    'id': new_dish.id_dish,
                    'name': new_dish.name,
                    'price': str(new_dish.price),
                    'image': new_dish.img,
                    'category_id': new_dish.id_category.id_category
                }
            }, status=201)

        except Exception as e:
            print(f"Ошибка при добавлении блюда: {e}")
            return JsonResponse({'success': False, 'error': 'Внутренняя ошибка сервера.'}, status=500)

    return JsonResponse({'success': False, 'error': 'Метод не разрешён.'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_category_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Название категории обязательно.'}, status=400)

        try:
            category = Category.objects.create(name=name)
            return JsonResponse({
                'success': True,
                'category': {'id': category.id_category, 'name': category.name}
            })
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'Категория с таким названием уже существует.'}, status=400)
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Только POST-запросы разрешены.'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_category_view(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')

        if not category_id:
            return JsonResponse({'success': False, 'error': 'ID категории не передан.'}, status=400)

        try:
            category = get_object_or_404(Category, id_category=category_id)
            if category.dishes.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Невозможно удалить категорию, так как с ней связаны блюда.'
                }, status=400)

            category.delete()
            return JsonResponse({'success': True})

        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Категория не найдена.'}, status=404)
        except ProtectedError:
            return JsonResponse({
                'success': False,
                'error': 'Невозможно удалить категорию, так как с ней связаны другие данные.'
            }, status=400)
        except Exception as e:
            print(f"Ошибка при удалении категории {category_id}: {e}")
            return JsonResponse({'success': False, 'error': 'Внутренняя ошибка сервера.'}, status=500)

    return JsonResponse({'success': False, 'error': 'Только POST-запросы разрешены.'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_dish_view(request, dish_id):
    if request.method == 'POST':
        try:
            dish = get_object_or_404(Dish, id_dish=dish_id)
            dish_name = dish.name
            dish.delete()
            messages.success(request, f"Блюдо '{dish_name}' успешно удалено.")
            return redirect('admin_menu')

        except Dish.DoesNotExist:
            messages.error(request, "Блюдо не найдено.")
            return redirect('admin_menu')
        except Exception as e:
            print(f"Ошибка при удалении блюда {dish_id}: {e}")
            messages.error(request, f"Ошибка при удалении блюда '{dish_id}': {e}")

            return redirect('admin_menu')

    return HttpResponse("Метод не разрешён.", status=405)


from django.db.models import Sum, F
from decimal import Decimal


@user_passes_test(lambda u: u.is_superuser)
def admin_orders_today_view(request):
    today = datetime.now().date()

    orders = Ordr.objects.filter(delivery_date=today).select_related('id_company')

    order_list = []
    for order in orders:
        total_amount = OrdrItem.objects.filter(
            id_ordr=order
        ).aggregate(
            total=Sum(F('quantity') * F('id_dish__price'))
        )['total'] or Decimal('0.00')

        order_list.append({
            'id': order.id_order,
            'company': order.id_company.name,
            'address': order.delivery_address,
            'phone': order.id_company.phone,
            'amount': total_amount,
            'time': order.delivery_time.strftime('%H:%M') if order.delivery_time else '—',
            'status': order.status
        })

    return render(request, 'admin_orders_by_date.html', {
        'title': 'Заказы на сегодня',
        'orders': order_list
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_orders_tomorrow_view(request):
    tomorrow = datetime.now().date() + timedelta(days=1)

    orders = Ordr.objects.filter(delivery_date=tomorrow).select_related('id_company')

    order_list = []
    for order in orders:
        total_amount = OrdrItem.objects.filter(
            id_ordr=order
        ).aggregate(
            total=Sum(F('quantity') * F('id_dish__price'))
        )['total'] or Decimal('0.00')

        order_list.append({
            'id': order.id_order,
            'company': order.id_company.name,
            'address': order.delivery_address,
            'phone': order.id_company.phone,
            'amount': total_amount,
            'time': order.delivery_time.strftime('%H:%M') if order.delivery_time else '—',
            'status': order.status
        })

    return render(request, 'admin_orders_by_date.html', {
        'title': 'Заказы на завтра',
        'orders': order_list
    })


@login_required
def create_order_view(request):
    if request.method == 'POST':
        selected_date_str = request.session.get('selected_date')
        if not selected_date_str:
            return JsonResponse({'success': False, 'error': 'Дата доставки не выбрана'})

        try:
            company = Company.objects.get(email=request.user.email)
            all_carts = request.session.get('carts', {})
            cart_items = all_carts.get(selected_date_str, [])

            if not cart_items:
                return JsonResponse({'success': False, 'error': 'Корзина пуста'})

            delivery_address = request.POST.get('address')
            delivery_time = request.POST.get('time')

            if not delivery_address or not delivery_time:
                return JsonResponse({'success': False, 'error': 'Заполните адрес и время доставки'})

            with transaction.atomic():
                order = Ordr.objects.create(
                    id_company=company,
                    delivery_date=selected_date_str,
                    delivery_time=delivery_time,
                    delivery_address=delivery_address,
                    status='новый'
                )

                for item in cart_items:
                    dish = Dish.objects.get(id_dish=item['id'])
                    OrdrItem.objects.create(
                        id_ordr=order,
                        id_dish=dish,
                        quantity=item['quantity']
                    )

                if selected_date_str in all_carts:
                    del all_carts[selected_date_str]
                    request.session['carts'] = all_carts
                    request.session.modified = True

                return JsonResponse({'success': True, 'order_id': order.id_order})

        except Company.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Компания не найдена'})
        except Exception as e:
            print(f"Ошибка создания заказа: {e}")
            return JsonResponse({'success': False, 'error': f'Ошибка оформления заказа: {str(e)}'})

    return JsonResponse({'success': False, 'error': 'Метод не разрешен'})