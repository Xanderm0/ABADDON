from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Productos.models import Categoria, Producto
from Usuarios.models import Usuario
from Ventas.models import Venta

# -------------------- VALIDACIÓN DE ROL --------------------
def is_admin(user):
    """Verifica si el usuario tiene rol de Administrador."""
    return user.is_authenticated and user.rol == 'Administrador'

def is_vendedor(user):
    """Verifica si el usuario es Vendedor o Administrador."""
    return user.is_authenticated and (user.rol == 'Vendedor' or user.rol == 'Administrador')

def is_admin_vendedor(user):
    return user.is_authenticated and user.rol in ['Administrador', 'Vendedor']

# -------------------- INICIO --------------------
def home(request):
    """Página de inicio pública con productos destacados y categorías activas."""
    productos_destacados = Producto.objects.filter(estado=True, stock__gt=0).select_related('categoria').order_by('nombre')[:4]
    categorias = Categoria.objects.filter(estado=True).order_by('nombre_categoria')[:4]

    return render(request, 'home.html', {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
    })

def quienes_somos(request):
    return render(request, 'quienes_somos.html')

# -------------------- DASHBOARD --------------------
STOCK_INSUFICIENTE_LIMITE = 5

@login_required
def dashboard(request):
    # REPORTE DE PRODUCTOS

    productos_sin_stock = Producto.objects.select_related('categoria').filter(
        stock=0
    ).order_by('nombre')

    productos_stock_insuficiente = Producto.objects.select_related('categoria').filter(
        stock__gt=0,
        stock__lte=STOCK_INSUFICIENTE_LIMITE
    ).order_by('stock', 'nombre')

    productos_en_venta = Producto.objects.select_related('categoria').filter(
        estado=True,
        stock__gt=STOCK_INSUFICIENTE_LIMITE
    ).order_by('nombre')

    # REPORTE DE USUARIOS

    usuarios_activos_lista = Usuario.objects.filter(estado=True).order_by('nombre')
    usuarios_inactivos_lista = Usuario.objects.filter(estado=False).order_by('nombre')

    context = {
        # Resumen general
        'total_productos': Producto.objects.count(),
        'productos_activos': productos_en_venta.count(),
        'productos_sin_stock': productos_sin_stock.count(),

        'total_categorias': Categoria.objects.count(),

        'total_usuarios': Usuario.objects.count(),
        'usuarios_activos': usuarios_activos_lista.count(),

        'total_ventas': Venta.objects.count(),
        'ventas_activas': Venta.objects.count(),

        # Últimos registros
        'ultimos_productos': Producto.objects.select_related('categoria').order_by('-id_producto')[:5],
        'ultimas_ventas': Venta.objects.order_by('-fecha')[:5],

        # Análisis de productos
        'productos_sin_stock_lista': productos_sin_stock,
        'productos_stock_insuficiente_lista': productos_stock_insuficiente,
        'productos_en_venta_lista': productos_en_venta,

        'total_productos_sin_stock': productos_sin_stock.count(),
        'total_productos_stock_insuficiente': productos_stock_insuficiente.count(),
        'total_productos_en_venta': productos_en_venta.count(),

        'limite_stock_insuficiente': STOCK_INSUFICIENTE_LIMITE,

        # Análisis de usuarios
        'usuarios_activos_lista': usuarios_activos_lista,
        'usuarios_inactivos_lista': usuarios_inactivos_lista,

        'total_usuarios_activos': usuarios_activos_lista.count(),
        'total_usuarios_inactivos': usuarios_inactivos_lista.count(),
    }

    return render(request, 'dashboard/dashboard.html', context)