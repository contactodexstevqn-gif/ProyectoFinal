from django.contrib import admin
from django.urls import path, include
from . import views
from ventas import views as ventas_views

urlpatterns = [
    path('', views.login_view, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('admin/', admin.site.urls),
    path('venta/', ventas_views.nueva_venta, name='nueva_venta'),
    path('exportar-ventas/', ventas_views.exportar_ventas, name='exportar_ventas'),
    path('productos/', include('productos.urls')),
]