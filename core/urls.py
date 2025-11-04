# core/urls.py
from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=True)),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('cart/', views.cart_view, name='cart'),
    # path('menu/', views.admin_menu_view, name='admin_menu'),
    path('menu/', views.menu_view, name='menu'),
    path('dish/<int:dish_id>/', views.dish_detail_view, name='dish_detail'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('receipt/', views.receipt_view, name='receipt'),
    path('faq/', views.faq_view, name='faq'),
    path('profile/', views.profile_view, name='profile'),
    path('agreement/', views.agreement_view, name='agreement'),

    path('admin/menu/', views.admin_menu_view, name='admin_menu'),
    path('admin/category/add/', views.add_category_view, name='add_category'),
    path('admin/dish/<int:dish_id>/', views.admin_dish_detail_view, name='admin_dish_detail'),
]