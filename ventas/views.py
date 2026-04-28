from django.shortcuts import render, redirect
from productos.models import Producto
from .models import Venta
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.http import HttpResponse


@login_required(login_url='login')
def nueva_venta(request):
    productos = Producto.objects.all()
    error = None

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad'))

        producto = Producto.objects.get(id=producto_id)

        if cantidad <= 0:
            error = "La cantidad debe ser mayor a 0"

        elif cantidad > producto.stock:
            error = "No hay suficiente stock disponible"

        else:
            Venta.objects.create(
                producto=producto,
                vendedor=request.user,
                cantidad=cantidad
            )

            return redirect('dashboard')

    return render(request, 'nueva_venta.html', {
        'productos': productos,
        'error': error
    })


@login_required(login_url='login')
def exportar_ventas(request):
    ventas = Venta.objects.select_related('producto', 'vendedor').all()

    data = []

    for v in ventas:
        data.append({
            'Producto': v.producto.nombre,
            'Cantidad': v.cantidad,
            'Total': v.total,
            'Vendedor': v.vendedor.username if v.vendedor else '',
            'Fecha': v.fecha.strftime('%d/%m/%Y %I:%M %p'),
        })

    df = pd.DataFrame(data)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = 'attachment; filename=ventas.xlsx'

    df.to_excel(response, index=False)

    return response