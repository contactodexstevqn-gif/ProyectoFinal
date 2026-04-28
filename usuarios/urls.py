from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.iniciarSesion, name='login'),
    path('logout/', views.cerrarSesion, name='logout'),
    path('usuarios/', views.gestionUsuarios, name='usuarios'),
]