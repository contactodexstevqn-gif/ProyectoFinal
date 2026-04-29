from django.urls import path
from . import views

urlpatterns = [
    path('nueva/', views.nueva_venta, name='nueva_venta'),
    path('exportar/', views.exportar_ventas, name='exportar_ventas'),
]