from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.urls import reverse
from datetime import datetime, timedelta

def login_view(request):
    if request.user.is_authenticated:
        return redirect('calendar')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('calendar')
        else:
            return HttpResponse("Неверный логин или пароль")
    else:
        return render(request, 'login.html')

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

@login_required
def cart_view(request):
    cart_items = request.session.get('cart', [])

    total = sum(item['quantity'] * item['price'] for item in cart_items)

    if not cart_items:
        cart_items = None

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
        'item_count': len(cart_items) if cart_items else 0
    })
@login_required
def update_cart(request):
    if request.method == 'POST':
        dish_id = request.POST.get('dish_id')
        quantity = request.POST.get('quantity')
        remove = request.POST.get('remove')

        cart = request.session.get('cart', [])

        if remove == 'true' or (quantity and int(quantity) <= 0):
            cart = [item for item in cart if item['id'] != dish_id]
        elif quantity:
            for item in cart:
                if item['id'] == dish_id:
                    item['quantity'] = int(quantity)
                    break

        request.session['cart'] = cart

    return redirect('cart')

@login_required
def menu_view(request):
    dishes = [
        {
            'id': 1,
            'name': 'Блюдо 1',
            'price': 250,
            'image': 'https://via.placeholder.com/300x200?text=Блюдо+1'
        },
        {
            'id': 2,
            'name': 'Блюдо 2',
            'price': 320,
            'image': 'https://via.placeholder.com/300x200?text=Блюдо+2'
        },
        {
            'id': 3,
            'name': 'Блюдо 3',
            'price': 180,
            'image': 'https://via.placeholder.com/300x200?text=Блюдо+3'
        },
        {
            'id': 4,
            'name': 'Блюдо 4',
            'price': 450,
            'image': 'https://via.placeholder.com/300x200?text=Блюдо+4'
        },
        {
            'id': 5,
            'name': 'Блюдо 5',
            'price': 290,
            'image': 'https://via.placeholder.com/300x200?text=Блюдо+5'
        },
        {
            'id': 6,
            'name': 'Блюдо 6',
            'price': 380,
            'image': 'https://via.placeholder.com/300x200?text=Блюдо+6'
        },
        {
            'id': 7,
            'name': 'Блюдо 7',
            'price': 250,
            'image': 'https://via.placeholder.com/300x200?text=Блюдо+7'
        },
        {
            'id': 8,
            'name': 'Блюдо 8',
            'price': 320,
            'image': 'https://via.placeholder.com/300x200?text=Блюдо+8'
        },
        {
            'id': 9,
            'name': 'Блюдо 9',
            'price': 180,
            'image': 'https://via.placeholder.com/300x200?text=Блюдо+9'
        },
        {
            'id': 10,
            'name': 'Блюдо 10',
            'price': 450,
            'image': 'https://via.placeholder.com/300x200?text=Блюдо+10'
        },
        {
            'id': 11,
            'name': 'Блюдо 11',
            'price': 290,
            'image': 'https://via.placeholder.com/300x200?text=Блюдо+11'
        },
        {
            'id': 12,
            'name': 'Блюдо 12',
            'price': 380,
            'image': 'https://via.placeholder.com/300x200?text=Блюдо+12'
        },
    ]

    return render(request, 'menu.html', {'dishes': dishes})

@login_required
def dish_detail_view(request, dish_id):
    dishes = [
        {
            'id': 1,
            'name': 'Плов',
            'price': 250,
            'image': 'https://via.placeholder.com/300x200?text=Плов',
            'description': 'Состоит из нескольких компонентов, объединённых в единую порцию. Каждый элемент располагается в определённой и взаимодействует с другими в пределах общей структуры.'
        },
        {
            'id': 2,
            'name': 'Борщ',
            'price': 320,
            'image': 'https://via.placeholder.com/300x200?text=Борщ',
            'description': 'Традиционный славянский суп из свеклы, капусты, мяса и специй. Готовится долго, но результат того стоит.'
        },
        {
            'id': 3,
            'name': 'Салат Цезарь',
            'price': 180,
            'image': 'https://via.placeholder.com/300x200?text=Цезарь',
            'description': 'Классический салат с курицей, сухариками, пармезаном и соусом Цезарь. Идеально подходит для легкого перекуса.'
        },
        {
            'id': 4,
            'name': 'Пицца Маргарита',
            'price': 450,
            'image': 'https://via.placeholder.com/300x200?text=Пицца',
            'description': 'Итальянская пицца с томатным соусом, моцареллой и базиликом. Простота и вкус в одном блюде.'
        },
        {
            'id': 5,
            'name': 'Оливье',
            'price': 290,
            'image': 'https://via.placeholder.com/300x200?text=Оливье',
            'description': 'Новогодний салат из картофеля, моркови, огурцов, яиц и колбасы. Всегда радует своим вкусом.'
        },
        {
            'id': 6,
            'name': 'Суп-пюре из тыквы',
            'price': 380,
            'image': 'https://via.placeholder.com/300x200?text=Тыква',
            'description': 'Кремовый суп из спелой тыквы с сливками и специями. Тепло и уютно в холодный день.'
        },
    ]

    dish = next((d for d in dishes if d['id'] == int(dish_id)), None)
    if not dish:
        return HttpResponse("Блюдо не найдено", status=404)

    return render(request, 'dish_detail.html', {'dish': dish})

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        dish_id = request.POST.get('dish_id')
        dish_name = request.POST.get('dish_name')
        dish_price = request.POST.get('dish_price')
        dish_image = request.POST.get('dish_image')
        quantity = int(request.POST.get('quantity', 1))

        cart = request.session.get('cart', [])

        found = False
        for item in cart:
            if item['id'] == dish_id:
                item['quantity'] += quantity
                found = True
                break

        if not found:
            cart.append({
                'id': dish_id,
                'name': dish_name,
                'price': float(dish_price),
                'image': dish_image,
                'quantity': quantity
            })

        request.session['cart'] = cart

        return redirect('menu')

    return redirect('menu')

@login_required
def receipt_view(request):
    cart_items = request.session.get('cart', [])

    total = 0
    for item in cart_items:
        item_total = item['price'] * item['quantity']
        item['total_price'] = item_total
        total += item_total

    selected_date_str = request.session.get('selected_date')
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

    return render(request, 'profile.html')

@login_required
def agreement_view(request):
    return render(request, 'agreement.html')