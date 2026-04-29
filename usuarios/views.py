from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

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