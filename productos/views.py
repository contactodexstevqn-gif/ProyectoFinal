import json

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from backend.permissions import admin_required
from .forms import CategoriaForm, ProductoForm
from .models import Categoria, Producto, MovimientoInventario

from django.contrib import messages


@login_required(login_url='login')
@admin_required
def listar_productos(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    stock = request.GET.get('stock', '')

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
        productos = productos.filter(stock__gte=1, stock__lte=5)
    elif stock == 'sin_stock':
        productos = productos.filter(stock=0)

    total_productos = Producto.objects.count()
    stock_bajo = Producto.objects.filter(stock__gte=1, stock__lte=5).count()
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
    })


@login_required(login_url='login')
@admin_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('productos')
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
            form.save()
            return redirect('agregar_categoria')
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
        form = ProductoForm(request.POST, instance=producto)

        if form.is_valid():
            form.save()
            return redirect('productos')
    else:
        form = ProductoForm(instance=producto)

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
        motivo = request.POST.get('motivo')
        cantidad = request.POST.get('cantidad')
        observacion = request.POST.get('observacion', '')

        if not tipo or not motivo or not cantidad:
            messages.error(request, 'Debes completar tipo de movimiento, motivo y cantidad.')
            return redirect('actualizar_stock', producto_id=producto.id)

        try:
            cantidad = int(cantidad)
        except ValueError:
            messages.error(request, 'La cantidad debe ser un numero valido')
            return redirect('actualizar_stock', producto_id=producto.id)

        if cantidad < 0:
            messages.error(request, 'La cantidad del stock no puede ser negativa')
            return redirect('actualizar_stock', producto_id=producto.id)

        stock_anterior = producto.stock

        if tipo == 'entrada':
            stock_nuevo = stock_anterior + cantidad

        elif tipo == 'salida':
            stock_nuevo = stock_anterior - cantidad

            if stock_nuevo < 0:
                messages.error(request, 'El stock no puede quedar negativo, no puedes sacar mas' \
                'productos de los que hay actualmente')
                return redirect('actualizar_stock', producto_id=producto.id)

        elif tipo == 'correccion':
            stock_nuevo = cantidad

        else:
            messages.error(request, 'El tipo de movimiento no es valido')
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

        messages.success(request, 'Stock actualizado correctamente')
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
            producto.delete()
            return redirect('productos')
        else:
            return render(request, 'eliminar_producto.html', 
                          {'producto': producto,
                           'error': 'Debes confirmar la eliminación para continuar.'})
        
    return render(request, 'eliminar_producto.html', {
        'producto': producto})

@login_required(login_url='login')
@admin_required
def inventario(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    stock = request.GET.get('stock', '')

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
        productos = productos.filter(stock__gte=1, stock__lte=5)
    elif stock == 'sin_stock':
        productos = productos.filter(stock=0)
    elif stock == 'disponible':
        productos = productos.filter(stock__gt=5)

    productos_lista = list(productos)

    for producto in productos_lista:
        producto.valor_stock = producto.precio * producto.stock

    todos_productos = Producto.objects.all()

    total_productos = Producto.objects.count()
    stock_bajo = Producto.objects.filter(stock__gte=1, stock__lte=5).count()
    sin_stock = Producto.objects.filter(stock=0).count()
    disponibles = Producto.objects.filter(stock__gt=5).count()
    valor_total = sum(producto.precio * producto.stock for producto in todos_productos)

    productos_criticos = Producto.objects.select_related('categoria').filter(stock__lte=5).order_by('stock', 'nombre')[:5]

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
    })

# Todo lo no relacionado con catalogo publico, hacen el codigo arriba de este comentario 
# de aqui para abajo es backend para la pagina publica del catalogo

def catalogo_publico(request):
    productos = Producto.objects.select_related('categoria').all().order_by('nombre')

    return render(request, 'catalogo.html', {'productos': productos})
