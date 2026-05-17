from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from backend.pagination import OPCIONES_POR_PAGINA, obtener_por_pagina, parametros_sin_pagina
from backend.permissions import (
    GRUPO_VENDEDOR,
    admin_required,
    asegurar_grupos_base,
    es_administrador,
    rol_usuario,
)
from .forms import VendedorForm, VendedorEditForm


def iniciarSesion(request):
    if request.method == 'POST':
        nombreUsuario = request.POST.get('username')
        contraseña = request.POST.get('password')

        usuario = authenticate(request, username=nombreUsuario, password=contraseña)

        if usuario is not None:
            login(request, usuario)
            return redirect('dashboard')
        else:
            return render(request, 'public/login.html', {
                'error': 'Cuenta no encontrada'
            })

    return render(request, 'public/login.html')


def cerrarSesion(request):
    logout(request)
    return redirect('login')


@login_required
@admin_required
def gestionUsuarios(request):
    usuarios = User.objects.filter(is_superuser=False).order_by('-date_joined')

    total_usuarios = usuarios.count()
    usuarios_activos = usuarios.filter(is_active=True).count()
    usuarios_inactivos = usuarios.filter(is_active=False).count()

    per_page, per_page_int = obtener_por_pagina(request)
    paginator = Paginator(usuarios, per_page_int)
    pagina = request.GET.get('page')
    usuarios_pagina = paginator.get_page(pagina)
    query_params = parametros_sin_pagina(request, ['page'])

    return render(request, 'usuarios/usuarios.html', {
        'usuarios': usuarios_pagina,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
        'es_admin': es_administrador(request.user),
        'rol_usuario': rol_usuario(request.user),
        'query_params': query_params,
        'per_page': per_page,
        'per_page_options': OPCIONES_POR_PAGINA,
    })


@login_required
@admin_required
def crearVendedor(request):
    asegurar_grupos_base()

    if request.method == 'POST':
        form = VendedorForm(request.POST)

        if form.is_valid():
            vendedor = form.save(commit=False)

            contra = form.cleaned_data.get('contra')
            vendedor.set_password(contra)

            vendedor.is_superuser = False
            vendedor.is_staff = False
            vendedor.is_active = True

            vendedor.save()

            grupo_vendedor = Group.objects.get(name=GRUPO_VENDEDOR)
            vendedor.groups.add(grupo_vendedor)

            messages.success(request, 'Usuario creado correctamente.')
            return redirect('usuarios')
    else:
        form = VendedorForm()

    return render(request, 'usuarios/crear_vendedor.html', {
        'form': form,
        'es_admin': es_administrador(request.user),
        'rol_usuario': rol_usuario(request.user),
    })

@login_required
@admin_required
def editarVendedor(request, usuario_id):
    vendedor = get_object_or_404(User, id=usuario_id, is_superuser=False)

    if request.method == 'POST':
        form = VendedorEditForm(request.POST, instance=vendedor)

        if form.is_valid():
            form.save()
            messages.success(request, f'El vendedor {vendedor.username} fue actualizado correctamente.')
            return redirect('usuarios')

        messages.error(request, 'No se pudo actualizar el vendedor. Revisa los datos ingresados.')
    else:
        form = VendedorEditForm(instance=vendedor)

    return render(request, 'usuarios/editar_vendedor.html', {
        'form': form,
        'vendedor': vendedor,
        'es_admin': es_administrador(request.user),
        'rol_usuario': rol_usuario(request.user),
    })

@login_required
@admin_required
def cambiarEstadoUsuario(request, usuario_id):
    if request.method != 'POST':
        return redirect('usuarios')

    usuario = get_object_or_404(User, id=usuario_id, is_superuser=False)

    if usuario == request.user:
        messages.error(request, 'No puedes desactivar tu propio usuario.')
        return redirect('usuarios')

    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=['is_active'])

    if usuario.is_active:
        messages.success(request, f'El usuario {usuario.username} fue activado correctamente.')
    else:
        messages.success(request, f'El usuario {usuario.username} fue desactivado correctamente.')

    return redirect('usuarios')
