from django.urls import path
from . import views

urlpatterns = [
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('categorias/', views.agregar_categoria, name='agregar_categoria'),
]