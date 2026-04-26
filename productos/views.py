from django.shortcuts import render, redirect
from django.http import JsonResponse
#from django.contrib.auth.decorators import login_required
import json

from .forms import ProductoForm, CategoriaForm
from .models import Categoria


#@login_required
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


#@login_required
def agregar_categoria(request):
    categorias = Categoria.objects.all()

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


def crear_categoria(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()

        if not nombre:
            return JsonResponse({
                'success': False,
                'error': 'El nombre es obligatorio'
            })

        categoria, creada = Categoria.objects.get_or_create(nombre=nombre)

        return JsonResponse({
            'success': True,
            'id': categoria.id,
            'nombre': categoria.nombre,
            'creada': creada
        })

    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })