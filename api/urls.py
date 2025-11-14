# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('dishes', views.DishViewSet)
router.register('companies', views.CompanyViewSet)
router.register('orders', views.OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('user/orders/', views.get_user_orders, name='user_orders'),
    path('orders/create/', views.create_order, name='create_order'),
]