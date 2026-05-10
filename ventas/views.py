from datetime import datetime, time, timedelta
from decimal import InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
import pandas as pd

from backend.permissions import es_administrador, rol_usuario
from productos.models import Producto
from .models import Venta


def rango_dia(fecha):
    zona = timezone.get_current_timezone()

    inicio = datetime.combine(fecha, time.min)
    fin = inicio + timedelta(days=1)

    if timezone.is_naive(inicio):
        inicio = timezone.make_aware(inicio, zona)

    if timezone.is_naive(fin):
        fin = timezone.make_aware(fin, zona)

    return inicio, fin


def rango_mes(fecha):
    zona = timezone.get_current_timezone()

    inicio = datetime(fecha.year, fecha.month, 1)

    if fecha.month == 12:
        fin = datetime(fecha.year + 1, 1, 1)
    else:
        fin = datetime(fecha.year, fecha.month + 1, 1)

    if timezone.is_naive(inicio):
        inicio = timezone.make_aware(inicio, zona)

    if timezone.is_naive(fin):
        fin = timezone.make_aware(fin, zona)

    return inicio, fin


def ventas_permitidas(usuario, es_admin):
    ventas = Venta.objects.select_related(
        'producto',
        'producto__categoria',
        'vendedor'
    )

    if not es_admin:
        ventas = ventas.filter(vendedor=usuario)

    return ventas


def aplicar_filtros_ventas(request, ventas, es_admin):
    query = request.GET.get('q', '').strip()
    fecha = request.GET.get('fecha', '').strip()
    vendedor_id = request.GET.get('vendedor', '').strip()

    if query:
        ventas = ventas.filter(
            Q(producto__nombre__icontains=query) |
            Q(producto__categoria__nombre__icontains=query) |
            Q(producto__color__icontains=query) |
            Q(producto__talla__icontains=query) |
            Q(vendedor__username__icontains=query)
        )

    if fecha:
        fecha_filtro = parse_date(fecha)

        if fecha_filtro:
            inicio_fecha, fin_fecha = rango_dia(fecha_filtro)

            ventas = ventas.filter(
                fecha__gte=inicio_fecha,
                fecha__lt=fin_fecha
            )

    if es_admin and vendedor_id:
        ventas = ventas.filter(vendedor_id=vendedor_id)

    return ventas, query, fecha, vendedor_id


def vendedores_con_ventas():
    vendedores_ids = Venta.objects.values_list(
        'vendedor_id',
        flat=True
    ).distinct()

    return User.objects.filter(
        id__in=vendedores_ids
    ).order_by('username')


@login_required(login_url='login')
def nueva_venta(request):
    es_admin = es_administrador(request.user)

    productos = Producto.objects.select_related('categoria').all().order_by('nombre')
    productos_disponibles = productos.filter(stock__gt=0)

    error = None

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad_raw = request.POST.get('cantidad')

        try:
            cantidad = int(cantidad_raw)
        except (TypeError, ValueError):
            cantidad = 0

        if not producto_id:
            error = 'Debes seleccionar un producto.'
        elif cantidad <= 0:
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
                    return redirect('nueva_venta')

                except (ValueError, InvalidOperation, ValidationError):
                    error = 'No se pudo registrar la venta. Revisa los datos e intenta de nuevo.'

    ventas_base = ventas_permitidas(request.user, es_admin)

    ventas_recientes = ventas_base.order_by('-fecha')[:5]

    hoy = timezone.localdate()

    inicio_hoy, fin_hoy = rango_dia(hoy)
    inicio_mes, fin_mes = rango_mes(hoy)

    ventas_hoy = ventas_base.filter(
        fecha__gte=inicio_hoy,
        fecha__lt=fin_hoy
    )

    ventas_mes = ventas_base.filter(
        fecha__gte=inicio_mes,
        fecha__lt=fin_mes
    )

    total_ventas = ventas_base.aggregate(total=Sum('total'))['total'] or 0
    total_hoy = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0
    total_mes = ventas_mes.aggregate(total=Sum('total'))['total'] or 0
    unidades_vendidas = ventas_base.aggregate(total=Sum('cantidad'))['total'] or 0

    return render(request, 'nueva_venta.html', {
        'productos': productos,
        'productos_disponibles': productos_disponibles,
        'ventas_recientes': ventas_recientes,
        'error': error,
        'es_admin': es_admin,
        'rol_usuario': rol_usuario(request.user),
        'total_ventas': total_ventas,
        'total_hoy': total_hoy,
        'total_mes': total_mes,
        'unidades_vendidas': unidades_vendidas,
    })


@login_required(login_url='login')
def historial_ventas(request):
    es_admin = es_administrador(request.user)

    ventas_base = ventas_permitidas(request.user, es_admin)

    ventas_filtradas, query, fecha, vendedor_id = aplicar_filtros_ventas(
        request,
        ventas_base,
        es_admin
    )

    total_filtrado = ventas_filtradas.aggregate(total=Sum('total'))['total'] or 0
    unidades_filtradas = ventas_filtradas.aggregate(total=Sum('cantidad'))['total'] or 0
    cantidad_ventas = ventas_filtradas.count()

    ventas = ventas_filtradas.order_by('-fecha')

    vendedores = vendedores_con_ventas() if es_admin else User.objects.none()

    return render(request, 'historial_ventas.html', {
        'ventas': ventas,
        'vendedores': vendedores,
        'query': query,
        'fecha': fecha,
        'vendedor_id': vendedor_id,
        'es_admin': es_admin,
        'rol_usuario': rol_usuario(request.user),
        'total_filtrado': total_filtrado,
        'unidades_filtradas': unidades_filtradas,
        'cantidad_ventas': cantidad_ventas,
    })


@login_required(login_url='login')
def exportar_ventas(request):
    es_admin = es_administrador(request.user)

    ventas_base = ventas_permitidas(request.user, es_admin)

    ventas_filtradas, query, fecha, vendedor_id = aplicar_filtros_ventas(
        request,
        ventas_base,
        es_admin
    )

    ventas = ventas_filtradas.order_by('-fecha')

    if es_admin:
        nombre_archivo = 'historial_ventas.xlsx'
    else:
        nombre_archivo = 'mis_ventas.xlsx'

    data = []

    for venta in ventas:
        data.append({
            'Producto': venta.producto.nombre,
            'Categoria': venta.producto.categoria.nombre if venta.producto.categoria else 'Sin categoria',
            'Color': venta.producto.color,
            'Talla': venta.producto.talla,
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