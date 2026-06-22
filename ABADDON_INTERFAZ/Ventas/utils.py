from django.db.models import Q

from Productos.models import Producto
from .models import Venta


def obtener_tipos_venta_disponibles():
    """Devuelve los tipos de venta del modelo y también los valores antiguos existentes en BD."""
    tipos = list(Venta.TIPO_VENTA)
    valores_registrados = Venta.objects.exclude(
        tipo_venta__isnull=True
    ).exclude(
        tipo_venta=''
    ).values_list(
        'tipo_venta', flat=True
    ).distinct().order_by('tipo_venta')

    valores_en_choices = {valor for valor, _ in tipos}

    for valor in valores_registrados:
        if valor not in valores_en_choices:
            tipos.append((valor, valor.replace('_', ' ').title()))
            valores_en_choices.add(valor)

    return tipos


def aplicar_filtros_ventas(request, ventas):
    """Aplica a un queryset de ventas exactamente los mismos filtros usados en la tabla."""
    query = request.GET.get('q', '').strip()
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()
    selected_tipo_venta = request.GET.get('tipo_venta', '').strip()
    selected_metodo_pago = request.GET.get('metodo_pago', '').strip()
    selected_estado = request.GET.get('estado', '').strip()

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

    if selected_tipo_venta:
        ventas = ventas.filter(tipo_venta=selected_tipo_venta)

    if selected_metodo_pago:
        ventas = ventas.filter(metodo_pago_id=selected_metodo_pago)

    if selected_estado == 'activa':
        ventas = ventas.filter(estado=True)
    elif selected_estado == 'anulada':
        ventas = ventas.filter(estado=False)

    filtros = {
        'query': query,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'selected_tipo_venta': selected_tipo_venta,
        'selected_metodo_pago': selected_metodo_pago,
        'selected_estado': selected_estado,
    }

    return ventas, filtros


def devolver_stock_venta(venta):
    """
    Devuelve al inventario las cantidades de una venta.
    Debe llamarse solo cuando la venta todavía está activa.
    """
    unidades_reintegradas = 0

    for detalle in venta.detalles.select_related('producto').all():
        producto = Producto.objects.select_for_update().get(pk=detalle.producto_id)
        producto.stock += detalle.cantidad
        producto.save(update_fields=['stock'])
        unidades_reintegradas += detalle.cantidad

    return unidades_reintegradas
