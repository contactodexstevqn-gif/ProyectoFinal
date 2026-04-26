from django.contrib import admin
from django.urls import path, include
from ventas import views as ventas_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),

    path('venta/', ventas_views.nueva_venta, name='nueva_venta'),
    path('exportar-ventas/', ventas_views.exportar_ventas, name='exportar_ventas'),

    path('productos/', include('productos.urls')),
]