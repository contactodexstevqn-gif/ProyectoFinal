from datetime import datetime, time, timedelta
from math import floor, log10

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date

from backend.permissions import GRUPO_ADMINISTRADOR, admin_required, es_administrador, rol_usuario
from productos.models import Categoria, Producto
from ventas.models import Cliente, Venta


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


def vendedores_registrados():
    return User.objects.filter(
        is_active=True
    ).exclude(
        is_superuser=True
    ).exclude(
        groups__name=GRUPO_ADMINISTRADOR
    ).distinct().order_by('first_name', 'last_name', 'username')


def obtener_filtros_reportes(request):
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()
    vendedor_id = request.GET.get('vendedor', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()
    producto_id = request.GET.get('producto', '').strip()
    tipo_reporte = request.GET.get('tipo_reporte', 'general').strip() or 'general'

    return {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'vendedor_id': vendedor_id,
        'categoria_id': categoria_id,
        'producto_id': producto_id,
        'tipo_reporte': tipo_reporte,
    }


def ventas_filtradas_reportes(request, ventas):
    filtros = obtener_filtros_reportes(request)

    fecha_inicio_parseada = parse_date(filtros['fecha_inicio']) if filtros['fecha_inicio'] else None
    fecha_fin_parseada = parse_date(filtros['fecha_fin']) if filtros['fecha_fin'] else None

    if fecha_inicio_parseada:
        inicio, _ = rango_dia(fecha_inicio_parseada)
        ventas = ventas.filter(fecha__gte=inicio)

    if fecha_fin_parseada:
        _, fin = rango_dia(fecha_fin_parseada)
        ventas = ventas.filter(fecha__lt=fin)

    if filtros['vendedor_id']:
        ventas = ventas.filter(vendedor_id=filtros['vendedor_id'])

    if filtros['categoria_id']:
        ventas = ventas.filter(producto__categoria_id=filtros['categoria_id'])

    if filtros['producto_id']:
        ventas = ventas.filter(producto_id=filtros['producto_id'])

    return ventas, filtros


def formato_eje_pesos(valor):
    valor = int(valor or 0)

    if valor >= 1000000:
        numero = valor / 1000000

        if numero.is_integer():
            return f'${int(numero)}M'

        return f'${round(numero, 1)}M'.replace('.', ',')

    if valor >= 1000:
        numero = valor / 1000

        if numero.is_integer():
            return f'${int(numero)}K'

        return f'${round(numero, 1)}K'.replace('.', ',')

    return f'${valor}'


def formato_corto_pesos(valor):
    valor = int(valor or 0)

    if valor >= 1000000:
        numero = valor / 1000000

        if numero.is_integer():
            return f'${int(numero)}M'

        return f'${round(numero, 1)}M'.replace('.', ',')

    if valor >= 1000:
        numero = valor / 1000

        if numero.is_integer():
            return f'${int(numero)}K'

        return f'${round(numero)}K'

    return f'${valor}'


def calcular_maximo_eje(valor_maximo):
    valor_maximo = float(valor_maximo or 0)

    if valor_maximo <= 0:
        return 100000

    valor_maximo = valor_maximo * 1.12
    potencia = 10 ** floor(log10(valor_maximo))
    normalizado = valor_maximo / potencia

    if normalizado <= 1:
        escala = 1
    elif normalizado <= 2:
        escala = 2
    elif normalizado <= 5:
        escala = 5
    else:
        escala = 10

    return int(escala * potencia)


def construir_escala_y(maximo_eje):
    return [
        formato_eje_pesos(maximo_eje),
        formato_eje_pesos(maximo_eje * 5 / 6),
        formato_eje_pesos(maximo_eje * 4 / 6),
        formato_eje_pesos(maximo_eje * 3 / 6),
        formato_eje_pesos(maximo_eje * 2 / 6),
        formato_eje_pesos(maximo_eje * 1 / 6),
        '$0',
    ]


def calcular_porcentaje(actual, anterior):
    actual = float(actual or 0)
    anterior = float(anterior or 0)

    if anterior <= 0:
        return 0

    porcentaje = ((actual - anterior) / anterior) * 100
    return round(porcentaje, 1)


def construir_grafica_meses(ventas):
    hoy = timezone.localdate()
    meses = []

    for i in range(5, -1, -1):
        mes = hoy.month - i
        year = hoy.year

        while mes <= 0:
            mes += 12
            year -= 1

        inicio = datetime(year, mes, 1)

        if mes == 12:
            fin = datetime(year + 1, 1, 1)
        else:
            fin = datetime(year, mes + 1, 1)

        inicio = timezone.make_aware(inicio, timezone.get_current_timezone())
        fin = timezone.make_aware(fin, timezone.get_current_timezone())

        total = ventas.filter(
            fecha__gte=inicio,
            fecha__lt=fin
        ).aggregate(
            total=Sum('total')
        )['total'] or 0

        meses.append({
            'nombre': inicio.strftime('%b %Y'),
            'total': total,
        })

    maximo_real = max([float(mes['total'] or 0) for mes in meses] + [0])
    maximo_eje = calcular_maximo_eje(maximo_real)
    escala_y = construir_escala_y(maximo_eje)

    puntos = []

    for index, mes in enumerate(meses):
        total = float(mes['total'] or 0)
        x = 20 + (index * 112)
        proporcion = total / maximo_eje if maximo_eje > 0 else 0
        y = 230 - (proporcion * 210)

        puntos.append(f'{x} {y}')

        mes['left'] = round(4 + ((index / 5) * 92), 2) if len(meses) > 1 else 50
        mes['bottom'] = round(proporcion * 82, 2)

    line_path = 'M' + ' L'.join(puntos) if puntos else ''

    if puntos:
        primer_x = 20
        ultimo_x = 20 + ((len(meses) - 1) * 112)
        area_path = line_path + f' L{ultimo_x} 230 L{primer_x} 230 Z'
    else:
        area_path = ''

    return meses, line_path, area_path, escala_y


def construir_donut_categorias(categorias):
    colores = ['#d41473', '#ff7b8a', '#8b5cf6', '#f6c453', '#22c55e', '#0ea5e9']
    total_general = sum(float(categoria['total'] or 0) for categoria in categorias)

    if total_general <= 0:
        return '', []

    inicio = 0
    partes = []
    resultado = []

    for index, categoria in enumerate(categorias[:6]):
        total = float(categoria['total'] or 0)
        porcentaje = round((total / total_general) * 100, 1)
        fin = inicio + porcentaje
        color = colores[index % len(colores)]

        partes.append(f'{color} {inicio}% {fin}%')

        resultado.append({
            'nombre': categoria['producto__categoria__nombre'] or 'Sin categoría',
            'total': categoria['total'],
            'porcentaje': porcentaje,
            'color': color,
        })

        inicio = fin

    return ', '.join(partes), resultado


@login_required(login_url='login')
@admin_required
def reportes(request):
    ventas_base = Venta.objects.select_related(
        'producto',
        'producto__categoria',
        'vendedor',
        'cliente'
    )

    ventas, filtros = ventas_filtradas_reportes(request, ventas_base)

    hoy = timezone.localdate()
    inicio_mes, fin_mes = rango_mes(hoy)

    if hoy.month == 1:
        fecha_mes_anterior = hoy.replace(year=hoy.year - 1, month=12)
    else:
        fecha_mes_anterior = hoy.replace(month=hoy.month - 1)

    inicio_mes_anterior, fin_mes_anterior = rango_mes(fecha_mes_anterior)

    ventas_mes_actual = ventas_base.filter(
        fecha__gte=inicio_mes,
        fecha__lt=fin_mes
    )

    ventas_mes_anterior = ventas_base.filter(
        fecha__gte=inicio_mes_anterior,
        fecha__lt=fin_mes_anterior
    )

    ventas_totales = ventas.aggregate(total=Sum('total'))['total'] or 0
    ingresos_mes = ventas_mes_actual.aggregate(total=Sum('total'))['total'] or 0
    ingresos_mes_anterior = ventas_mes_anterior.aggregate(total=Sum('total'))['total'] or 0
    productos_vendidos = ventas.aggregate(total=Sum('cantidad'))['total'] or 0

    clientes_nuevos = Cliente.objects.filter(
        fecha_registro__gte=inicio_mes,
        fecha_registro__lt=fin_mes
    ).count()

    cantidad_ventas = ventas.count()
    ticket_promedio = ventas_totales / cantidad_ventas if cantidad_ventas > 0 else 0

    porcentaje_mes = calcular_porcentaje(ingresos_mes, ingresos_mes_anterior)
    porcentaje_ventas = porcentaje_mes
    porcentaje_productos = 0
    porcentaje_clientes = 0

    ventas_meses, ventas_meses_line_path, ventas_meses_area_path, escala_y = construir_grafica_meses(ventas_base)

    categorias_ventas_raw = list(
        ventas.values('producto__categoria__nombre')
        .annotate(total=Sum('total'))
        .order_by('-total')[:6]
    )

    donut_gradient, ventas_categorias = construir_donut_categorias(categorias_ventas_raw)

    top_productos_raw = list(
        ventas.values('producto__nombre')
        .annotate(
            cantidad=Sum('cantidad'),
            total=Sum('total')
        )
        .order_by('-cantidad')[:5]
    )

    max_top = max([item['cantidad'] or 0 for item in top_productos_raw] + [1])
    top_productos = []

    for item in top_productos_raw:
        top_productos.append({
            'nombre': item['producto__nombre'],
            'cantidad': item['cantidad'] or 0,
            'total': item['total'] or 0,
            'porcentaje': max(12, round(((item['cantidad'] or 0) / max_top) * 100)),
        })

    categoria_top = 'Sin datos'

    if ventas_categorias:
        categoria_top = f"{ventas_categorias[0]['nombre']} ({ventas_categorias[0]['porcentaje']}%)"

    vendedor_top_raw = (
        ventas.values('vendedor__username')
        .annotate(total=Sum('total'))
        .order_by('-total')
        .first()
    )

    vendedor_top = 'Sin datos'

    if vendedor_top_raw:
        vendedor_top = f"{vendedor_top_raw['vendedor__username']} ({formato_corto_pesos(vendedor_top_raw['total'])})"

    productos_stock_critico = Producto.objects.filter(stock__lte=5).count()

    vendedores = vendedores_registrados()
    categorias = Categoria.objects.all().order_by('nombre')
    productos = Producto.objects.select_related('categoria').all().order_by('nombre')

    return render(request, 'reportes.html', {
        'fecha_inicio': filtros['fecha_inicio'],
        'fecha_fin': filtros['fecha_fin'],
        'vendedor_id': filtros['vendedor_id'],
        'categoria_id': filtros['categoria_id'],
        'producto_id': filtros['producto_id'],
        'tipo_reporte': filtros['tipo_reporte'],
        'vendedores': vendedores,
        'categorias': categorias,
        'productos': productos,
        'ventas_totales': ventas_totales,
        'ingresos_mes': ingresos_mes,
        'productos_vendidos': productos_vendidos,
        'clientes_nuevos': clientes_nuevos,
        'porcentaje_ventas': porcentaje_ventas,
        'porcentaje_mes': porcentaje_mes,
        'porcentaje_productos': porcentaje_productos,
        'porcentaje_clientes': porcentaje_clientes,
        'ventas_meses': ventas_meses,
        'ventas_meses_line_path': ventas_meses_line_path,
        'ventas_meses_area_path': ventas_meses_area_path,
        'escala_y': escala_y,
        'donut_gradient': donut_gradient,
        'ventas_categorias': ventas_categorias,
        'top_productos': top_productos,
        'categoria_top': categoria_top,
        'ticket_promedio': ticket_promedio,
        'vendedor_top': vendedor_top,
        'productos_stock_critico': productos_stock_critico,
        'es_admin': es_administrador(request.user),
        'rol_usuario': rol_usuario(request.user),
    })