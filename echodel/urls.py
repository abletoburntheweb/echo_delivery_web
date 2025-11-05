# echodel/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core import views

urlpatterns = [
    path('admin/dish/update/<int:dish_id>/', views.update_dish, name='update_dish'),
    path('admin/calendar/', views.admin_calendar_view, name='admin_calendar'),
    path('admin/cart/', views.cart_view, name='admin_cart'),
    path('admin/menu/', views.admin_menu_view, name='admin_menu'),
    path('admin/dish/<int:dish_id>/', views.admin_dish_detail_view, name='admin_dish_detail'),
    path('admin/category/add/', views.add_category_view, name='add_category'),
    path('admin/category/delete/', views.delete_category_view, name='delete_category'),
    path('admin/dish/add/', views.add_dish_view, name='add_dish'),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)