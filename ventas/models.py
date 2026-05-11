from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction

from productos.models import MovimientoInventario, Producto


class Venta(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='ventas'
    )
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a 0.')

        if self.pk:
            self.total = self.producto.precio * self.cantidad
            super().save(*args, **kwargs)
            return

        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(pk=self.producto_id)

            if producto.stock < self.cantidad:
                raise ValueError('No hay suficiente stock disponible.')

            stock_anterior = producto.stock
            stock_nuevo = stock_anterior - self.cantidad

            self.producto = producto
            self.total = producto.precio * self.cantidad

            producto.stock = stock_nuevo
            producto.save(update_fields=['stock'])

            super().save(*args, **kwargs)

            MovimientoInventario.objects.create(
                producto=producto,
                tipo='salida',
                motivo='venta_sistema',
                cantidad=self.cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                observacion=f'Venta registrada #{self.pk}'
            )

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad}'