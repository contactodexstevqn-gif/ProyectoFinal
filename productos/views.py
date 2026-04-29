import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from backend.permissions import admin_required
from .forms import CategoriaForm, ProductoForm
from .models import Categoria


@login_required(login_url='login')
@admin_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('dashboard')
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
