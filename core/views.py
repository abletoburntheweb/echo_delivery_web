from PIL.Image import Image
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import ProtectedError
from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from datetime import datetime, timedelta
from .models import Dish, Category
from django.core.exceptions import ValidationError
from django.db import IntegrityError

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
    
    
    
    dishes = Dish.objects.select_related('category').all()
    return render(request, 'menu.html', {'dishes': dishes})






@login_required
def dish_detail_view(request, dish_id):
    print(f"Запрошенное dish_id: {dish_id}")
    
    

    
    dish = get_object_or_404(Dish, id=dish_id) 
    print(f"Найдено блюдо из базы: {dish}")
    
    return render(request, 'dish_detail.html', {'dish': dish})

@user_passes_test(lambda u: u.is_superuser)
def admin_dish_detail_view(request, dish_id):
    print(f"admin_dish_detail_view вызвана для dish_id: {dish_id}")
    
    

    
    dish = get_object_or_404(Dish, id=dish_id) 
    

    
    

    

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

        
        try:
            dish_obj = Dish.objects.get(id=dish_id)
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
    
    return render(request, 'admin_menu.html', {'dishes': dishes, 'categories': categories})

@login_required
@user_passes_test(lambda u: u.is_superuser) 
def update_dish(request, dish_id): 
    if request.method == 'POST':
        try:
            dish = get_object_or_404(Dish, id=dish_id)

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

            if new_image_file and not errors:
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
                dish.image = new_image_file

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
            if not image_file:
                errors.append("Поле 'Изображение' обязательно.")

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
                    category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    errors.append("Выбранная категория не существует.")

            if image_file and not errors:
                try:
                    img = Image.open(image_file)
                    img.verify()
                    image_file.seek(0)
                except Exception:
                    errors.append("Загруженный файл не является изображением.")

            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=400)

            new_dish = Dish.objects.create(
                name=name,
                description=description,
                price=price,
                category=category,
                image=image_file
            )

            return JsonResponse({
                'success': True,
                'message': 'Блюдо успешно добавлено!',
                'dish': {
                    'id': new_dish.id,
                    'name': new_dish.name,
                    'price': str(new_dish.price),
                    'image': new_dish.image.url,
                    'category_id': new_dish.category.id
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
                'category': {'id': category.id, 'name': category.name}
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
            category = get_object_or_404(Category, id=category_id)
            if category.dish_set.exists():
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