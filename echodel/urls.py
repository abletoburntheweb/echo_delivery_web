"""
URL configuration for echodel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from core import views

urlpatterns = [
    path('admin/calendar/', views.admin_calendar_view, name='admin_calendar'),
    path('admin/cart/', views.cart_view, name='admin_cart'),
    path('admin/menu/', views.admin_menu_view, name='admin_menu'),
    path('admin/dish/<int:dish_id>/', views.admin_dish_detail_view, name='admin_dish_detail'),
    #path('admin/receipt/', views.admin_receipt_view, name='admin_receipt'),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
