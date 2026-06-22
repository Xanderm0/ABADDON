from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.db.models import Q

from Productos.models import Producto, Categoria
from Ventas.models import MetodoPago, Venta
from Ventas.utils import aplicar_filtros_ventas
from Usuarios.models import Usuario
from General.views import is_admin, is_admin_vendedor

from .utils import render_to_pdf

# PANEL CENTRAL DE REPORTES

@user_passes_test(is_admin)
def reportes(request):
    """
    Muestra la vista del reporte general del sistema.
    Solo puede acceder el administrador.
    """
    return render(request, 'reportes/reportes.html')

# ----- REPORTES INDIVIDUALES -----
@login_required
def export_pdf_table(request, model_name):
    """
    Genera reportes PDF individuales según el modelo solicitado.

    Puede usarse desde:
    - producto_admin_list.html
    - categoria_list.html
    - venta_list.html
    - usuario_list.html

    También recibe filtros por GET.
    """

    query = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    rol = request.GET.get('rol', '').strip()
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()

    precio_min = request.GET.get('precio_min', '').strip()
    precio_max = request.GET.get('precio_max', '').strip()
    stock_min = request.GET.get('stock_min', '').strip()
    stock_max = request.GET.get('stock_max', '').strip()

    context = {
        'model_type': model_name,
    }

    template = 'reportes/table_pdf.html'

    # ----- REPORTE DE PRODUCTOS -----
    if model_name == 'productos':
        if not is_admin_vendedor(request.user):
            return redirect('dashboard')

        items = Producto.objects.select_related('categoria').all().order_by('nombre')

        if query:
            items = items.filter(
                Q(nombre__icontains=query)
                | Q(descripcion__icontains=query)
                | Q(categoria__nombre_categoria__icontains=query)
            )

        if categoria:
            items = items.filter(categoria_id=categoria)

        if estado == 'activo':
            items = items.filter(estado=True)
        elif estado == 'inactivo':
            items = items.filter(estado=False)

        if precio_min:
            items = items.filter(precio__gte=precio_min)

        if precio_max:
            items = items.filter(precio__lte=precio_max)

        if stock_min:
            items = items.filter(stock__gte=stock_min)

        if stock_max:
            items = items.filter(stock__lte=stock_max)

        context['items'] = items
        context['title'] = 'Reporte de Productos'
        context['filtros'] = {
            'query': query,
            'estado': estado,
            'categoria': categoria,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'stock_min': stock_min,
            'stock_max': stock_max,
        }

        return render_to_pdf(
            template,
            context,
            filename='reporte_productos.pdf'
        )

    # ----- REPORTE DE CATEGORÍAS -----
    elif model_name == 'categorias':
        if not is_admin_vendedor(request.user):
            return redirect('dashboard')

        items = Categoria.objects.all().order_by('nombre_categoria')

        if query:
            items = items.filter(
                Q(nombre_categoria__icontains=query)
                | Q(descripcion__icontains=query)
            )

        if estado == 'activo':
            items = items.filter(estado=True)
        elif estado == 'inactivo':
            items = items.filter(estado=False)

        context['items'] = items
        context['title'] = 'Reporte de Categorías'

        return render_to_pdf(
            template,
            context,
            filename='reporte_categorias.pdf'
        )

    # ----- REPORTE DE VENTAS -----

    elif model_name == 'ventas':
        if not is_admin_vendedor(request.user):
            return redirect('dashboard')

        items = Venta.objects.select_related(
            'empleado',
            'metodo_pago'
        ).prefetch_related(
            'detalles__producto'
        ).all().order_by('-fecha')

        items, _ = aplicar_filtros_ventas(request, items)

        context['items'] = items
        context['title'] = 'Reporte de Ventas'

        return render_to_pdf(
            template,
            context,
            filename='reporte_ventas.pdf'
        )

    # ----- REPORTE DE MÉTODOS DE PAGO -----
    elif model_name == 'metodos_pago':
        if not is_admin_vendedor(request.user):
            return redirect('dashboard')

        items = MetodoPago.objects.all().order_by('nombre')

        if query:
            items = items.filter(Q(nombre__icontains=query))

        if estado == 'activo':
            items = items.filter(estado=True)
        elif estado == 'inactivo':
            items = items.filter(estado=False)

        context['items'] = items
        context['title'] = 'Reporte de Métodos de Pago'

        return render_to_pdf(
            template,
            context,
            filename='reporte_metodos_pago.pdf'
        )

    # ----- REPORTE DE USUARIOS -----
    elif model_name == 'usuarios':
        if not is_admin(request.user):
            return redirect('dashboard')

        items = Usuario.objects.all().order_by('nombre')

        if query:
            items = items.filter(
                Q(nombre__icontains=query)
                | Q(email__icontains=query)
                | Q(rol__icontains=query)
            )

        if rol:
            items = items.filter(rol__iexact=rol)

        if estado == 'activo':
            items = items.filter(estado=True)
        elif estado == 'inactivo':
            items = items.filter(estado=False)

        context['items'] = items
        context['title'] = 'Reporte de Usuarios'

        return render_to_pdf(
            template,
            context,
            filename='reporte_usuarios.pdf'
        )

    return redirect('reportes')

# ----- REPORTE FILTRADO -----
@login_required
def export_pdf_filtrado(request):
    """
    Desde reportes.html solo se genera el reporte general.
    El filtro de estado se procesa dentro de export_pdf_general.
    """

    if not is_admin(request.user):
        return redirect('dashboard')

    return export_pdf_general(request)

# ----- REPORTE MULTITABLA -----
@user_passes_test(is_admin_vendedor)
def export_pdf_ventas_detalle(request):
    """
    Genera un reporte multitabla con:
    - Venta
    - Cliente
    - Empleado
    - Método de pago
    - Productos vendidos
    - Cantidad
    - Precio unitario
    - Subtotal
    - Total por venta
    """

    query = request.GET.get('q', '').strip()
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()

    ventas = Venta.objects.select_related(
        'empleado',
        'metodo_pago'
    ).prefetch_related(
        'detalles__producto'
    ).all().order_by('-fecha')

    ventas, _ = aplicar_filtros_ventas(request, ventas)

    ventas_reporte = []

    for venta in ventas:
        detalles = []
        total_venta = 0

        for detalle in venta.detalles.all():
            subtotal = detalle.cantidad * detalle.precio_unitario
            total_venta += subtotal

            detalles.append({
                'producto': detalle.producto,
                'cantidad': detalle.cantidad,
                'precio_unitario': detalle.precio_unitario,
                'subtotal': subtotal,
            })

        ventas_reporte.append({
            'venta': venta,
            'detalles': detalles,
            'total_venta': total_venta,
        })

    context = {
        'title': 'Reporte de Ventas con Detalle',
        'ventas_reporte': ventas_reporte,
    }

    return render_to_pdf(
        'reportes/ventas_detalle_pdf.html',
        context,
        filename='reporte_ventas_detalle.pdf'
    )

# ----- REPORTE MULTITABLA - PRODUCTO POR CATEGORÍA -----
@user_passes_test(is_admin_vendedor)
def export_pdf_inventario(request):
    """
    Genera un reporte multitabla de categorías con sus productos.
    """

    query = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()

    categorias = Categoria.objects.prefetch_related('producto_set').all().order_by('nombre_categoria')

    if query:
        categorias = categorias.filter(
            Q(nombre_categoria__icontains=query)
            | Q(descripcion__icontains=query)
            | Q(producto__nombre__icontains=query)
        ).distinct()

    if estado == 'activo':
        categorias = categorias.filter(estado=True)
    elif estado == 'inactivo':
        categorias = categorias.filter(estado=False)

    context = {
        'title': 'Reporte de Inventario por Categoría',
        'categorias': categorias,
    }

    return render_to_pdf(
        'reportes/inventario_pdf.html',
        context,
        filename='reporte_inventario.pdf'
    )

# ----- REPORTE GENERAL -----
@user_passes_test(is_admin)
def export_pdf_general(request):
    """
    Genera un reporte general del sistema.
    Permite filtrar por estado:
    - activo
    - inactivo
    - todos
    Solo puede acceder el administrador.
    """

    estado = request.GET.get('estado', '').strip().lower()

    usuarios = Usuario.objects.all().order_by('nombre')
    categorias = Categoria.objects.all().order_by('nombre_categoria')
    productos = Producto.objects.select_related('categoria').all().order_by('nombre')
    metodos_pago = MetodoPago.objects.all().order_by('nombre')

    ventas = Venta.objects.select_related(
        'empleado',
        'metodo_pago'
    ).prefetch_related(
        'detalles__producto'
    ).all().order_by('-fecha')

    if estado == 'activo':
        usuarios = usuarios.filter(estado=True)
        categorias = categorias.filter(estado=True)
        productos = productos.filter(estado=True)
        metodos_pago = metodos_pago.filter(estado=True)
        ventas = ventas.filter(estado=True)

    elif estado == 'inactivo':
        usuarios = usuarios.filter(estado=False)
        categorias = categorias.filter(estado=False)
        productos = productos.filter(estado=False)
        metodos_pago = metodos_pago.filter(estado=False)
        ventas = ventas.filter(estado=False)

    context = {
        'title': 'Reporte General Abaddon',
        'estado_filtro': estado,
        'usuarios': usuarios,
        'categorias': categorias,
        'productos': productos,
        'metodos_pago': metodos_pago,
        'ventas': ventas,
    }

    return render_to_pdf(
        'reportes/general_report.html',
        context,
        filename='reporte_general_abaddon.pdf'
    )