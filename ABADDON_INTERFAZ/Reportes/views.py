from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.db.models import Q

from Productos.models import Producto, Categoria
from Ventas.models import MetodoPago, Venta
from Usuarios.models import Usuario
from General.views import is_admin, is_admin_vendedor

from .utils import render_to_pdf

# PANEL CENTRAL DE REPORTES

@user_passes_test(is_admin_vendedor)
def reportes(request):
    """
    Muestra el panel central donde se pueden seleccionar reportes
    y aplicar filtros antes de descargar el PDF.
    """
    categorias = Categoria.objects.all().order_by('nombre_categoria')

    return render(request, 'reportes/reportes.html', {
        'categorias': categorias,
    })

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

        context['items'] = items
        context['title'] = 'Reporte de Productos'

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

        if query:
            items = items.filter(
                Q(nombre_cliente__icontains=query)
                | Q(email_cliente__icontains=query)
                | Q(empleado__nombre__icontains=query)
                | Q(metodo_pago__nombre__icontains=query)
                | Q(detalles__producto__nombre__icontains=query)
            ).distinct()

        if fecha_inicio:
            items = items.filter(fecha__date__gte=fecha_inicio)

        if fecha_fin:
            items = items.filter(fecha__date__lte=fecha_fin)

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
    Recibe el tipo de reporte desde reportes.html y redirige
    al generador correspondiente.
    """

    tipo_reporte = request.GET.get('tipo_reporte', '').strip()

    if tipo_reporte in ['productos', 'categorias', 'ventas', 'metodos_pago', 'usuarios']:
        return export_pdf_table(request, tipo_reporte)

    if tipo_reporte == 'ventas_detalle':
        return export_pdf_ventas_detalle(request)

    if tipo_reporte == 'general':
        if not is_admin(request.user):
            return redirect('dashboard')

        return export_pdf_general(request)

    return redirect('reportes')

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

    if query:
        ventas = ventas.filter(
            Q(nombre_cliente__icontains=query)
            | Q(email_cliente__icontains=query)
            | Q(empleado__nombre__icontains=query)
            | Q(metodo_pago__nombre__icontains=query)
            | Q(detalles__producto__nombre__icontains=query)
        ).distinct()

    if fecha_inicio:
        ventas = ventas.filter(fecha__date__gte=fecha_inicio)

    if fecha_fin:
        ventas = ventas.filter(fecha__date__lte=fecha_fin)

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
    Solo puede acceder el administrador.
    """

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

    context = {
        'title': 'Reporte General Abaddon',
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