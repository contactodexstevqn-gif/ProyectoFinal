from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F

from productos.models import Producto


class Venta(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='ventas'
    )
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a 0.')

        self.total = self.producto.precio * self.cantidad

        if self.pk:
            super().save(*args, **kwargs)
            return

        with transaction.atomic():
            actualizado = Producto.objects.filter(
                pk=self.producto_id,
                stock__gte=self.cantidad
            ).update(stock=F('stock') - self.cantidad)

            if actualizado == 0:
                raise ValueError('No hay suficiente stock disponible.')

            super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad}'