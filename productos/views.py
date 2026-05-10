import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from backend.permissions import admin_required
from configuracion.models import ConfiguracionTienda
from .forms import CategoriaForm, ProductoEditForm, ProductoForm
from .models import Categoria, Producto, MovimientoInventario


@login_required(login_url='login')
@admin_required
def listar_productos(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    stock = request.GET.get('stock', '')
    configuracion = ConfiguracionTienda.obtener()
    stock_minimo = configuracion.stock_minimo_alerta

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
            messages.success(request, f'Producto "{producto.nombre}" agregado correctamente.')
            return redirect('productos')
        else:
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
            messages.success(request, f'Categoría "{categoria.nombre}" agregada correctamente.')
            return redirect('agregar_categoria')
        else:
            messages.error(request, 'No se pudo agregar la categoría. Revisa los datos ingresados.')
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
            'error': 'Solicitud inválida.'
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
        else:
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
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        motivo = request.POST.get('motivo') or None
        cantidad = request.POST.get('cantidad')
        observacion = request.POST.get('observacion', '') or None

        if not tipo or not cantidad:
            messages.error(request, 'Debes completar tipo de movimiento y cantidad.')
            return redirect('actualizar_stock', producto_id=producto.id)

        try:
            cantidad = int(cantidad)
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return redirect('actualizar_stock', producto_id=producto.id)

        if cantidad < 0:
            messages.error(request, 'La cantidad del stock no puede ser negativa.')
            return redirect('actualizar_stock', producto_id=producto.id)

        stock_anterior = producto.stock

        if tipo == 'entrada':
            stock_nuevo = stock_anterior + cantidad

        elif tipo == 'salida':
            stock_nuevo = stock_anterior - cantidad

            if stock_nuevo < 0:
                messages.error(request, 'No puedes retirar más productos de los que hay actualmente.')
                return redirect('actualizar_stock', producto_id=producto.id)

        elif tipo == 'correccion':
            stock_nuevo = cantidad

        else:
            messages.error(request, 'El tipo de movimiento no es válido.')
            return redirect('actualizar_stock', producto_id=producto.id)

        producto.stock = stock_nuevo
        producto.save()

        MovimientoInventario.objects.create(
            producto=producto,
            tipo=tipo,
            motivo=motivo,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            observacion=observacion
        )

        messages.success(
            request,
            f'Stock de "{producto.nombre}" actualizado correctamente. Antes: {stock_anterior}, ahora: {stock_nuevo}.'
        )
        return redirect('inventario')

    return render(request, 'actualizar_stock.html', {
        'producto': producto,
        'tipoElecciones': MovimientoInventario.tipoElecciones,
        'motivoElecciones': MovimientoInventario.motivoElecciones,
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

        messages.error(request, 'Debes confirmar la eliminación para continuar.')
        return render(request, 'eliminar_producto.html', {
            'producto': producto,
            'error': 'Debes confirmar la eliminación para continuar.'
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
    configuracion = ConfiguracionTienda.obtener()
    stock_minimo = configuracion.stock_minimo_alerta

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
        stock__gte=1,
        stock__lte=stock_minimo
    ).order_by('stock', 'nombre')[:5]

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
