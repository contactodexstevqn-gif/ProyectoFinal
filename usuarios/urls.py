from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.iniciarSesion, name='login'),
    path('logout/', views.cerrarSesion, name='logout'),
    path('usuarios/', views.gestionUsuarios, name='usuarios'),
    path('usuarios/crear/', views.crearVendedor, name='crear_vendedor'),
    path('usuarios/<int:usuario_id>/editar/', views.editarVendedor, name='editar_vendedor'),
    path('usuarios/<int:usuario_id>/cambiar-estado/', views.cambiarEstadoUsuario, name='cambiar_estado_usuario'),
]