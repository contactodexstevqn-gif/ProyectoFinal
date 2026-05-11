import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from backend.permissions import admin_required
from configuracion.models import ConfiguracionTienda
from .forms import CategoriaForm, ProductoEditForm, ProductoForm
from .models import Categoria, MovimientoInventario, Producto


def obtener_stock_minimo():
    return ConfiguracionTienda.obtener().stock_minimo_alerta


@login_required(login_url='login')
@admin_required
def listar_productos(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    stock = request.GET.get('stock', '')
    stock_minimo = obtener_stock_minimo()

    productos = Producto.objects.select_related('categoria').all().order_by('nombre')
    categorias = Categoria.objects.all().order_by('nombre')

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(talla__icontains=query) |
            Q(color__icontains=query)
        )

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if stock == 'bajo':
        productos = productos.filter(stock__gte=1, stock__lte=stock_minimo)
    elif stock == 'sin_stock':
        productos = productos.filter(stock=0)

    total_productos = Producto.objects.count()
    stock_bajo = Producto.objects.filter(stock__gte=1, stock__lte=stock_minimo).count()
    sin_stock = Producto.objects.filter(stock=0).count()

    return render(request, 'productos.html', {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categoria_id': categoria_id,
        'stock': stock,
        'total_productos': total_productos,
        'stock_bajo': stock_bajo,
        'sin_stock': sin_stock,
        'stock_minimo_alerta': stock_minimo,
    })


@login_required(login_url='login')
@admin_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)

        if form.is_valid():
            producto = form.save()

            if producto.stock > 0:
                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo='entrada',
                    motivo='correccion_manual',
                    cantidad=producto.stock,
                    stock_anterior=0,
                    stock_nuevo=producto.stock,
                    observacion='Stock inicial al registrar el producto.'
                )

            messages.success(request, f'Producto "{producto.nombre}" agregado correctamente.')
            return redirect('productos')

        messages.error(request, 'No se pudo agregar el producto. Revisa los datos ingresados.')
    else:
        form = ProductoForm()

    return render(request, 'agregar_producto.html', {
        'form': form
    })


@login_required(login_url='login')
@admin_required
def agregar_categoria(request):
    categorias = Categoria.objects.all().order_by('nombre')

    if request.method == 'POST':
        form = CategoriaForm(request.POST)

        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria "{categoria.nombre}" agregada correctamente.')
            return redirect('agregar_categoria')

        messages.error(request, 'No se pudo agregar la categoria. Revisa los datos ingresados.')
    else:
        form = CategoriaForm()

    return render(request, 'agregar_categoria.html', {
        'form': form,
        'categorias': categorias
    })


@login_required(login_url='login')
@admin_required
@require_POST
def crear_categoria(request):
    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud invalida.'
        }, status=400)

    nombre = data.get('nombre', '').strip()

    if not nombre:
        return JsonResponse({
            'success': False,
            'error': 'El nombre es obligatorio.'
        }, status=400)

    categoria, creada = Categoria.objects.get_or_create(nombre=nombre)

    return JsonResponse({
        'success': True,
        'id': categoria.id,
        'nombre': categoria.nombre,
        'creada': creada
    })


@login_required(login_url='login')
@admin_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = ProductoEditForm(request.POST, request.FILES, instance=producto)

        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado correctamente.')
            return redirect('productos')

        messages.error(request, 'No se pudo actualizar el producto. Revisa los datos ingresados.')
    else:
        form = ProductoEditForm(instance=producto)

    return render(request, 'editar_producto.html', {
        'form': form,
        'producto': producto
    })


@login_required(login_url='login')
@admin_required
def actualizar_stock(request, producto_id):
    producto = get_object_or_404(
        Producto.objects.select_related('categoria'),
        id=producto_id
    )
    stock_minimo = obtener_stock_minimo()

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        motivo = request.POST.get('motivo') or None
        cantidad_raw = request.POST.get('cantidad')
        observacion = request.POST.get('observacion', '').strip() or None

        if not tipo or cantidad_raw in [None, '']:
            messages.error(request, 'Debes completar tipo de movimiento y cantidad.')
            return redirect('actualizar_stock', producto_id=producto.id)

        try:
            cantidad = int(cantidad_raw)
        except ValueError:
            messages.error(request, 'La cantidad debe ser un numero valido.')
            return redirect('actualizar_stock', producto_id=producto.id)

        if cantidad < 0:
            messages.error(request, 'La cantidad no puede ser negativa.')
            return redirect('actualizar_stock', producto_id=producto.id)

        if tipo in ['entrada', 'salida'] and cantidad == 0:
            messages.error(request, 'Para entradas o salidas la cantidad debe ser mayor a 0.')
            return redirect('actualizar_stock', producto_id=producto.id)

        if tipo not in ['entrada', 'salida', 'correccion']:
            messages.error(request, 'El tipo de movimiento no es valido.')
            return redirect('actualizar_stock', producto_id=producto.id)

        try:
            with transaction.atomic():
                producto_bloqueado = Producto.objects.select_for_update().get(id=producto.id)
                stock_anterior = producto_bloqueado.stock

                if tipo == 'entrada':
                    stock_nuevo = stock_anterior + cantidad
                    cantidad_movimiento = cantidad
                elif tipo == 'salida':
                    stock_nuevo = stock_anterior - cantidad
                    cantidad_movimiento = cantidad

                    if stock_nuevo < 0:
                        raise ValidationError('No puedes retirar mas productos de los que hay actualmente.')
                else:
                    stock_nuevo = cantidad
                    cantidad_movimiento = abs(stock_nuevo - stock_anterior)

                producto_bloqueado.stock = stock_nuevo
                producto_bloqueado.save(update_fields=['stock'])

                MovimientoInventario.objects.create(
                    producto=producto_bloqueado,
                    tipo=tipo,
                    motivo=motivo,
                    cantidad=cantidad_movimiento,
                    stock_anterior=stock_anterior,
                    stock_nuevo=stock_nuevo,
                    observacion=observacion
                )

            messages.success(
                request,
                f'Stock de "{producto.nombre}" actualizado correctamente. Antes: {stock_anterior}, ahora: {stock_nuevo}.'
            )
            return redirect('inventario')

        except ValidationError as error:
            messages.error(request, error.messages[0] if error.messages else 'No se pudo actualizar el stock.')
            return redirect('actualizar_stock', producto_id=producto.id)

    movimientos_producto = MovimientoInventario.objects.select_related(
        'producto',
        'producto__categoria'
    ).filter(
        producto=producto
    ).order_by('-fecha')[:10]

    return render(request, 'actualizar_stock.html', {
        'producto': producto,
        'tipoElecciones': MovimientoInventario.tipoElecciones,
        'motivoElecciones': MovimientoInventario.motivoElecciones,
        'movimientos_producto': movimientos_producto,
        'stock_minimo_alerta': stock_minimo,
    })


@login_required(login_url='login')
@admin_required
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        confirmar = request.POST.get('confirmar')

        if confirmar == 'si':
            nombre_producto = producto.nombre

            try:
                producto.delete()
            except ProtectedError:
                messages.error(
                    request,
                    f'No se puede eliminar "{nombre_producto}" porque tiene ventas registradas.'
                )
                return redirect('productos')

            messages.success(request, f'Producto "{nombre_producto}" eliminado correctamente.')
            return redirect('productos')

        messages.error(request, 'Debes confirmar la eliminacion para continuar.')
        return render(request, 'eliminar_producto.html', {
            'producto': producto,
            'error': 'Debes confirmar la eliminacion para continuar.'
        })

    return render(request, 'eliminar_producto.html', {
        'producto': producto
    })


@login_required(login_url='login')
@admin_required
def inventario(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    stock = request.GET.get('stock', '')
    stock_minimo = obtener_stock_minimo()

    productos = Producto.objects.select_related('categoria').all().order_by('stock', 'nombre')
    categorias = Categoria.objects.all().order_by('nombre')

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(talla__icontains=query) |
            Q(color__icontains=query)
        )

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if stock == 'bajo':
        productos = productos.filter(stock__gte=1, stock__lte=stock_minimo)
    elif stock == 'sin_stock':
        productos = productos.filter(stock=0)
    elif stock == 'disponible':
        productos = productos.filter(stock__gt=stock_minimo)

    productos_lista = list(productos)

    for producto in productos_lista:
        producto.valor_stock = producto.precio * producto.stock

    todos_productos = Producto.objects.all()

    total_productos = Producto.objects.count()
    stock_bajo = Producto.objects.filter(stock__gte=1, stock__lte=stock_minimo).count()
    sin_stock = Producto.objects.filter(stock=0).count()
    disponibles = Producto.objects.filter(stock__gt=stock_minimo).count()
    valor_total = sum(producto.precio * producto.stock for producto in todos_productos)

    productos_criticos = Producto.objects.select_related('categoria').filter(
        stock__gte=0,
        stock__lte=stock_minimo
    ).order_by('stock', 'nombre')[:8]

    movimientos_recientes = MovimientoInventario.objects.select_related(
        'producto',
        'producto__categoria'
    ).all().order_by('-fecha')[:50]

    total_movimientos = MovimientoInventario.objects.count()
    total_entradas = MovimientoInventario.objects.filter(tipo='entrada').count()
    total_salidas = MovimientoInventario.objects.filter(tipo='salida').count()
    total_correcciones = MovimientoInventario.objects.filter(tipo='correccion').count()

    return render(request, 'inventario.html', {
        'productos': productos_lista,
        'categorias': categorias,
        'query': query,
        'categoria_id': categoria_id,
        'stock': stock,
        'total_productos': total_productos,
        'stock_bajo': stock_bajo,
        'sin_stock': sin_stock,
        'disponibles': disponibles,
        'valor_total': valor_total,
        'productos_criticos': productos_criticos,
        'stock_minimo_alerta': stock_minimo,
        'movimientos_recientes': movimientos_recientes,
        'total_movimientos': total_movimientos,
        'total_entradas': total_entradas,
        'total_salidas': total_salidas,
        'total_correcciones': total_correcciones,
    })


@login_required(login_url='login')
@admin_required
def historial_inventario(request):
    query = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    motivo = request.GET.get('motivo', '').strip()
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()

    movimientos = MovimientoInventario.objects.select_related(
        'producto',
        'producto__categoria'
    ).all().order_by('-fecha')

    if query:
        movimientos = movimientos.filter(
            Q(producto__nombre__icontains=query) |
            Q(producto__categoria__nombre__icontains=query) |
            Q(producto__color__icontains=query) |
            Q(producto__talla__icontains=query) |
            Q(observacion__icontains=query)
        )

    if tipo:
        movimientos = movimientos.filter(tipo=tipo)

    if motivo:
        movimientos = movimientos.filter(motivo=motivo)

    fecha_inicio_parseada = parse_date(fecha_inicio) if fecha_inicio else None
    fecha_fin_parseada = parse_date(fecha_fin) if fecha_fin else None

    if fecha_inicio_parseada:
        movimientos = movimientos.filter(fecha__date__gte=fecha_inicio_parseada)

    if fecha_fin_parseada:
        movimientos = movimientos.filter(fecha__date__lte=fecha_fin_parseada)

    total_filtrado = movimientos.count()
    entradas_filtradas = movimientos.filter(tipo='entrada').count()
    salidas_filtradas = movimientos.filter(tipo='salida').count()
    correcciones_filtradas = movimientos.filter(tipo='correccion').count()

    paginator = Paginator(movimientos, 20)
    pagina = request.GET.get('page')
    movimientos_pagina = paginator.get_page(pagina)

    return render(request, 'historial_inventario.html', {
        'movimientos': movimientos_pagina,
        'query': query,
        'tipo': tipo,
        'motivo': motivo,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'tipoElecciones': MovimientoInventario.tipoElecciones,
        'motivoElecciones': MovimientoInventario.motivoElecciones,
        'total_filtrado': total_filtrado,
        'entradas_filtradas': entradas_filtradas,
        'salidas_filtradas': salidas_filtradas,
        'correcciones_filtradas': correcciones_filtradas,
    })


def catalogo_publico(request):
    configuracion = ConfiguracionTienda.obtener()
    stock_minimo = configuracion.stock_minimo_alerta
    productos = Producto.objects.select_related('categoria').all().order_by('nombre')
    telefono_whatsapp = ''.join(caracter for caracter in configuracion.telefono if caracter.isdigit()) or '573001234567'

    if not configuracion.mostrar_agotados_catalogo:
        productos = productos.filter(stock__gt=0)

    return render(request, 'catalogo.html', {
        'productos': productos,
        'stock_minimo_alerta': stock_minimo,
        'configuracion': configuracion,
        'telefono_whatsapp': telefono_whatsapp,
    })