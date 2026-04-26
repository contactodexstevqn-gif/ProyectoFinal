from django.db import models
from productos.models import Producto
from django.contrib.auth.models import User

class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total = self.producto.precio * self.cantidad

        if not self.pk:
            self.producto.stock -= self.cantidad
            self.producto.vendidos += self.cantidad
            self.producto.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"