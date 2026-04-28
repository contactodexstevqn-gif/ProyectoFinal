from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import VendedorForm

def iniciarSesion(request):
    if request.method == 'POST':
        nombreUsuario = request.POST.get('username')
        contraseña = request.POST.get('password')

        usuario = authenticate(request, username=nombreUsuario, password=contraseña)

        if usuario is not None:
            login(request, usuario)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {
                          'error':
                          'Cuenta no encontrada'
                          })
    return render (request, 'login.html')

def cerrarSesion(request):
    logout(request)
    return redirect('login')

@login_required
def gestionUsuarios(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    
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

            return redirect('usuarios')
    else:
         form = VendedorForm()

    vendedores = User.objects.filter(is_superuser=False)
    return render(request, 'usuarios.html', { 'vendedores': vendedores,
                                            'form': form})

