from django.contrib import admin
from .models import Producto, Categoria, MovimientoInventario

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'talla', 'color', 'precio', 'stock')
    search_fields = ('nombre', 'categoria__nombre', 'color')
    list_filter = ('categoria', 'talla', 'color')

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'tipo', 'motivo', 'cantidad', 'stock_anterior',
        'stock_nuevo', 'fecha',)

    search_fields = ('producto__nombre', 'motivo', 'observacion',)

    list_filter = ('tipo', 'motivo', 'fecha',)

    readonly_fields = ('fecha',)