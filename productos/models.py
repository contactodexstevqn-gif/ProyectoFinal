from django.db import models
from django.conf import settings


class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    talla = models.CharField(max_length=20)
    color = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    imagen = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class MovimientoInventario(models.Model):
    tipoElecciones = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('correccion', 'Correccion de stock'),
    ]

    motivoElecciones = [
    ('compra_proveedor', 'Compra a proveedor'),
    ('devolucion_cliente', 'Devolución de cliente'),
    ('venta_manual', 'Venta manual'),
    ('producto_dañado', 'Producto dañado'),
    ('perdida', 'Pérdida'),
    ('robo', 'Robo'),
    ('conteo_fisico', 'Conteo físico'),
    ('correccion_manual', 'Corrección manual'),
    ('devolucion_proveedor', 'Devolución a proveedor')
]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, 
                                 related_name='movimientos')
    
    tipo = models.CharField(max_length=15, choices=tipoElecciones)
    motivo = models.CharField(max_length=100, choices=motivoElecciones)
    cantidad = models.PositiveIntegerField()
    stock_anterior = models.PositiveIntegerField()
    stock_nuevo = models.PositiveIntegerField()
    observacion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.producto.nombre} - {self.tipo} - {self.cantidad}'

