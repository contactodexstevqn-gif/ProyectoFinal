from django.shortcuts import render
from productos.models import Producto
from ventas.models import Venta
from django.contrib.auth.models import User
from django.db.models import Sum, Q

def dashboard(request):
    query = request.GET.get('q', '')

    productos = Producto.objects.all()

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(categoria__nombre__icontains=query) |
            Q(color__icontains=query) |
            Q(talla__icontains=query)
        )

    productos = productos.annotate(
        total_vendidos=Sum('venta__cantidad')
    ).distinct().order_by('-total_vendidos', 'nombre')

    total_productos = Producto.objects.count()
    stock_bajo = Producto.objects.filter(stock__lte=5).count()
    total_ventas = Venta.objects.aggregate(total=Sum('total'))['total'] or 0
    total_clientes = User.objects.count()

    ventas_recientes = Venta.objects.select_related(
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
    })