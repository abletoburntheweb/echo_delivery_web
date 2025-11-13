# echodel/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core import views

urlpatterns = [
    path('admin/dish/update/<int:dish_id>/', views.update_dish, name='update_dish'),
    path('admin/panel/', views.admin_panel_view, name='admin_panel'),
    path('admin/clients/', views.admin_clients_view, name='admin_clients'),
    path('admin/calendar/', views.admin_calendar_view, name='admin_calendar'),
    path('admin/orders/', views.admin_orders_by_date_view, name='admin_orders_by_date'),
    path('admin/order/delete/<int:order_id>/', views.admin_delete_order_view, name='admin_delete_order'),
    path('admin/cart/', views.cart_view, name='admin_cart'),
    path('admin/menu/', views.admin_menu_view, name='admin_menu'),
    path('admin/dish/<int:dish_id>/', views.admin_dish_detail_view, name='admin_dish_detail'),
    path('admin/dish/delete/<int:dish_id>/', views.delete_dish_view, name='delete_dish'),
    path('admin/clients/delete/<int:company_id>/', views.delete_client_view, name='delete_client'),
    path('admin/client/<int:company_id>/orders/', views.admin_client_orders_view, name='admin_client_orders'),
    path('admin/category/add/', views.add_category_view, name='add_category'),
    path('admin/category/delete/', views.delete_category_view, name='delete_category'),
    path('admin/dish/list/', views.get_dishes_by_category, name='get_dishes_by_category'),
    path('admin/dish/add/', views.add_dish_view, name='add_dish'),
    path('admin/logout/', views.admin_logout_view, name='admin_logout'),

    path('admin/settings/save/', views.save_admin_settings, name='save_admin_settings'),
    path('admin/orders/today/', views.admin_orders_today_view, name='admin_orders_today'),
    path('admin/orders/tomorrow/', views.admin_orders_tomorrow_view, name='admin_orders_tomorrow'),
    path('admin/order/<int:order_id>/details/', views.get_order_details, name='order_details'),

    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)