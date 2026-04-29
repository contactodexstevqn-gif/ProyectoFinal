from decimal import InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
import pandas as pd

from productos.models import Producto
from .models import Venta
from backend.permissions import es_administrador


@login_required(login_url='login')
def nueva_venta(request):
    productos = Producto.objects.all().order_by('nombre')
    error = None

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad_raw = request.POST.get('cantidad')

        try:
            cantidad = int(cantidad_raw)
        except (TypeError, ValueError):
            cantidad = 0

        if cantidad <= 0:
            error = 'La cantidad debe ser mayor a 0.'
        else:
            producto = get_object_or_404(Producto, id=producto_id)

            if cantidad > producto.stock:
                error = 'No hay suficiente stock disponible.'
            else:
                try:
                    Venta.objects.create(
                        producto=producto,
                        vendedor=request.user,
                        cantidad=cantidad
                    )
                    messages.success(request, 'Venta registrada correctamente.')
                    return redirect('dashboard')
                except (ValueError, InvalidOperation):
                    error = 'No se pudo registrar la venta. Revisa los datos e intenta de nuevo.'

    return render(request, 'nueva_venta.html', {
        'productos': productos,
        'error': error
    })


@login_required(login_url='login')
def exportar_ventas(request):
    if es_administrador(request.user):
        ventas = Venta.objects.select_related('producto', 'vendedor').order_by('-fecha')
        nombre_archivo = 'ventas_completas.xlsx'
    else:
        ventas = Venta.objects.select_related('producto', 'vendedor').filter(vendedor=request.user).order_by('-fecha')
        nombre_archivo = 'mis_ventas.xlsx'

    data = []

    for venta in ventas:
        data.append({
            'Producto': venta.producto.nombre,
            'Cantidad': venta.cantidad,
            'Total': venta.total,
            'Vendedor': venta.vendedor.username if venta.vendedor else '',
            'Fecha': timezone.localtime(venta.fecha).strftime('%d/%m/%Y %I:%M %p'),
        })

    df = pd.DataFrame(data)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={nombre_archivo}'

    df.to_excel(response, index=False)
    return response
