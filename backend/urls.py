from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from productos.views import catalogo_publico
from ventas import views as ventas_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('formulario/', views.formulario, name='formulario'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('productos/', include('productos.urls')),
    path('configuracion/', include('configuracion.urls')),
    path('', include('usuarios.urls')),
    path('venta/', include('ventas.urls')),
    path('catalogo/', catalogo_publico, name='catalogo_publico'),
    path('reportes/', include('reportes.urls')),
    path('', views.index, name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
