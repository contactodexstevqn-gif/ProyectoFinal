import json

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from backend.permissions import admin_required
from .forms import CategoriaForm, ProductoForm
from .models import Categoria, Producto


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
        cantidad = request.POST.get('cantidad')

        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            cantidad = 0

        if cantidad > 0:
            producto.stock += cantidad
            producto.save()
            return redirect('productos')

    return render(request, 'actualizar_stock.html', {
        'producto': producto
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



# Todo lo no relacionado con catalogo publico, hacen el codigo arriba de este comentario de aqui para abajo
# es backend para la pagina publica cuando se haga despliegue 

def catalogo_publico(request):
    productos = Producto.objects.select_related('categoria').all().order_by('nombre')

    return render(request, 'catalogo.html', {'productos': productos})
