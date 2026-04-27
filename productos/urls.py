from django.urls import path
from . import views

urlpatterns = [
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('agregar-categoria/', views.agregar_categoria, name='agregar_categoria'),
    path('crear-categoria/', views.crear_categoria, name='crear_categoria'),
]