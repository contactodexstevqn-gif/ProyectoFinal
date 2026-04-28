from django.contrib import admin
from django.urls import path, include
from . import views
from ventas import views as ventas_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),

    path('', include('usuarios.urls')),
    path('productos/', include('productos.urls')),

    path('venta/', ventas_views.nueva_venta, name='nueva_venta'),
    path('exportar-ventas/', ventas_views.exportar_ventas, name='exportar_ventas'),
    path('usuarios/', views.usuarios, name='usuarios'),
]