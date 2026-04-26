from django.contrib import admin
from .models import Producto, Categoria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'talla', 'color', 'precio', 'stock')
    search_fields = ('nombre', 'categoria__nombre', 'color')
    list_filter = ('categoria', 'talla', 'color')