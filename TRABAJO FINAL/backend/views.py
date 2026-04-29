# BACKEND ES LA APP PRINCIPAL (DASHBOARD)

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.shortcuts import redirect, render

from productos.models import Producto
from ventas.models import Venta
from .permissions import es_administrador, rol_usuario


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if remember:
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)

            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'login.html')


@login_required(login_url='login')
def dashboard(request):
    query = request.GET.get('q', '')
    es_admin = es_administrador(request.user)

    productos = Producto.objects.all()

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(categoria__nombre__icontains=query) |
            Q(color__icontains=query) |
            Q(talla__icontains=query)
        )

    productos = productos.annotate(
        total_vendidos=Sum('ventas__cantidad')
    ).distinct().order_by('-total_vendidos', 'nombre')[:3]

    total_productos = Producto.objects.count()
    stock_bajo = Producto.objects.filter(stock__lte=5).count()

    if es_admin:
        ventas_base = Venta.objects.all()
        total_clientes = User.objects.count()
    else:
        ventas_base = Venta.objects.filter(vendedor=request.user)
        total_clientes = None

    total_ventas = ventas_base.aggregate(total=Sum('total'))['total'] or 0

    ventas_recientes = ventas_base.select_related(
        'producto',
        'vendedor'
    ).order_by('-id')[:5]

    return render(request, 'dashboard.html', {
        'query': query,
        'productos': productos,
        'ventas_recientes': ventas_recientes,
        'total_productos': total_productos,
        'stock_bajo': stock_bajo,
        'total_ventas': total_ventas,
        'total_clientes': total_clientes,
        'es_admin': es_admin,
        'rol_usuario': rol_usuario(request.user),
    })


@login_required(login_url='login')
def usuarios(request):
    if not es_administrador(request.user):
        messages.error(request, 'No tienes permisos para ver usuarios.')
        return redirect('dashboard')

    usuarios = User.objects.all().order_by('-date_joined')

    total_usuarios = usuarios.count()
    usuarios_activos = usuarios.filter(is_active=True).count()
    usuarios_inactivos = usuarios.filter(is_active=False).count()

    return render(request, 'usuarios.html', {
        'usuarios': usuarios,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
    })
