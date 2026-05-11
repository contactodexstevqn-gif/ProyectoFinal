from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from productos.views import catalogo_publico
from ventas import views as ventas_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('productos/', include('productos.urls')),
    path('configuracion/', include('configuracion.urls')),
    path('', include('usuarios.urls')),
    path('venta/', ventas_views.nueva_venta, name='nueva_venta'),
    path('historial-ventas/', ventas_views.historial_ventas, name='historial_ventas'),
    path('exportar-ventas/', ventas_views.exportar_ventas, name='exportar_ventas'),
    path('catalogo/', catalogo_publico, name='catalogo_publico'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
