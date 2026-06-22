from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.core.mail import send_mail
from django.db import transaction

from General.forms import VentaForm, CheckoutForm, MetodoPagoForm
from General.views import is_vendedor, is_admin
from .models import Venta, DetalleVenta, MetodoPago
from .utils import aplicar_filtros_ventas, devolver_stock_venta, obtener_tipos_venta_disponibles
from Productos.models import Producto
from Auditoria.models import Auditoria
from decimal import Decimal

# --- CARRITO DE COMPRAS ---
def _build_cart_context(request, form=None):
    """Construye el contexto del carrito sin duplicar cálculos entre vistas."""
    cart = request.session.get('cart', {})
    total = Decimal('0.00')
    cart_items = []

    for item_id, item_data in cart.items():
        price = Decimal(str(item_data.get('price', '0')))
        quantity = int(item_data.get('quantity', 0))
        subtotal = price * quantity
        total += subtotal
        cart_items.append({
            'id': item_id,
            'name': item_data.get('name', 'Producto'),
            'price': price,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    return {
        'cart_items': cart_items,
        'total': total,
        'metodos_pago': MetodoPago.objects.filter(estado=True).order_by('nombre'),
        'form': form or CheckoutForm(),
    }

def add_to_cart(request, product_id):
    """Añade un producto al carrito de compras usando sesiones de Django."""
    producto = get_object_or_404(Producto, id_producto=product_id)

    if not producto.estado or producto.stock <= 0:
        messages.error(request, f'{producto.nombre} no está disponible actualmente.')
        return redirect('catalogo')

    cart = request.session.get('cart', {})
    id_str = str(product_id)

    if id_str in cart:
        nueva_cantidad = cart[id_str]['quantity'] + 1
        if nueva_cantidad > producto.stock:
            messages.error(request, f'No hay suficiente stock para {producto.nombre}.')
        else:
            cart[id_str]['quantity'] = nueva_cantidad
            messages.success(request, f'Se agregó otra unidad de {producto.nombre}.')
    else:
        cart[id_str] = {
            'name': producto.nombre,
            'price': str(producto.precio),
            'quantity': 1,
        }
        messages.success(request, f'{producto.nombre} añadido al carrito.')

    request.session['cart'] = cart
    return redirect('view_cart')


def view_cart(request):
    """Muestra el contenido del carrito y calcula el total."""
    return render(request, 'cart.html', _build_cart_context(request))

def update_cart_quantity(request, product_id):
    """Actualiza la cantidad de un producto dentro del carrito."""
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id_producto=product_id)
        cart = request.session.get('cart', {})

        product_key = str(product_id)

        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

        if product_key not in cart:
            messages.warning(request, 'El producto no se encuentra en el carrito.')
            return redirect('view_cart')

        if quantity <= 0:
            del cart[product_key]
            messages.success(request, 'Producto eliminado del carrito.')
        else:
            if quantity > producto.stock:
                quantity = producto.stock
                messages.warning(
                    request,
                    f'Solo hay {producto.stock} unidades disponibles de {producto.nombre}.'
                )

            # Compatible si tu carrito guarda solo cantidad:
            # cart = {"1": 2, "3": 5}
            if isinstance(cart[product_key], int):
                cart[product_key] = quantity

            # Compatible si tu carrito guarda diccionarios:
            # cart = {"1": {"quantity": 2, "price": "50000"}}
            elif isinstance(cart[product_key], dict):
                cart[product_key]['quantity'] = quantity

            messages.success(request, 'Cantidad actualizada correctamente.')

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('view_cart')

def remove_from_cart(request, product_id):
    """Elimina un producto del carrito."""
    cart = request.session.get('cart', {})
    id_str = str(product_id)

    if id_str in cart:
        del cart[id_str]
        request.session['cart'] = cart
        messages.success(request, 'Producto eliminado del carrito.')

    return redirect('view_cart')

#  -------------- GESTIÓN DE VENTA --------------

@user_passes_test(is_vendedor)
def venta_list(request):
    """Lista ventas con los mismos filtros que se usan en los reportes PDF."""
    ventas_base = Venta.objects.select_related(
        'empleado',
        'metodo_pago'
    ).prefetch_related(
        'detalles__producto'
    ).all().order_by('-fecha')

    ventas, filtros = aplicar_filtros_ventas(request, ventas_base)

    context = {
        'ventas': ventas,
        'tipos_venta': obtener_tipos_venta_disponibles(),
        'metodos_pago': MetodoPago.objects.all().order_by('nombre'),
        'total_ventas_filtradas': ventas.count(),
    }
    context.update(filtros)

    return render(request, 'venta_list.html', context)

@user_passes_test(is_admin)
def venta_update(request, pk):
    """Permite corregir datos de una venta."""
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venta actualizada.')
            return redirect('venta_list')
    else:
        form = VentaForm(instance=venta)
    return render(request, 'crud/form.html', {'form': form, 'title': 'Editar Venta'})


@user_passes_test(is_vendedor)
@transaction.atomic
def venta_delete(request, pk):
    """Anula una venta, conserva su historial y devuelve el stock una sola vez."""
    venta = get_object_or_404(
        Venta.objects.select_for_update().prefetch_related('detalles__producto'),
        pk=pk
    )

    if request.method == 'POST':
        if not venta.estado:
            messages.warning(request, 'Esta venta ya estaba anulada. No se volvió a devolver stock.')
            return redirect('venta_list')

        unidades_reintegradas = devolver_stock_venta(venta)
        venta.estado = False
        venta.save(update_fields=['estado'])

        messages.success(
            request,
            f'Venta anulada correctamente. Se devolvieron {unidades_reintegradas} unidades al inventario.'
        )
        return redirect('venta_list')

    return render(request, 'crud/confirm_delete.html', {
        'obj': venta,
        'title': 'Anular Venta',
        'message': 'Esta acción anulará la venta, conservará el historial y devolverá al inventario las unidades vendidas. No uses esta opción para borrar pruebas o registros duplicados.',
        'button_text': 'Sí, anular venta',
        'cancel_url': 'venta_list',
    })


@user_passes_test(is_admin)
@transaction.atomic
def venta_delete_permanent(request, pk):
    """Elimina definitivamente una venta. Solo administrador."""
    venta = get_object_or_404(
        Venta.objects.select_for_update().prefetch_related('detalles__producto'),
        pk=pk
    )

    if request.method == 'POST':
        unidades_reintegradas = 0

        if venta.estado:
            unidades_reintegradas = devolver_stock_venta(venta)

        venta.delete()

        if unidades_reintegradas:
            messages.success(
                request,
                f'Venta eliminada definitivamente. Como estaba activa, se devolvieron {unidades_reintegradas} unidades al inventario.'
            )
        else:
            messages.success(request, 'Venta eliminada definitivamente.')

        return redirect('venta_list')

    return render(request, 'crud/confirm_delete.html', {
        'obj': venta,
        'title': 'Eliminar Venta Definitivamente',
        'message': 'Esta acción borrará la venta y sus detalles de la base de datos. Úsala solo para registros de prueba, duplicados o errores reales de captura. Si la venta está activa, primero se devolverá su stock.',
        'button_text': 'Sí, eliminar definitivamente',
        'cancel_url': 'venta_list',
    })

@user_passes_test(is_vendedor)
def detalle_venta(request, pk):
    venta = get_object_or_404(
        Venta.objects.select_related('empleado', 'metodo_pago').prefetch_related('detalles__producto'),
        id_venta=pk
    )

    detalles_venta = []
    total_venta = 0

    for detalle in venta.detalles.all():
        subtotal = detalle.cantidad * detalle.precio_unitario
        total_venta += subtotal

        detalles_venta.append({
            'producto': detalle.producto,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.precio_unitario,
            'subtotal': subtotal,
        })

    return render(request, 'detalle_venta.html', {
        'venta': venta,
        'detalles_venta': detalles_venta,
        'total_venta': total_venta,
    })

# -------------- MÉTODO DE PAGO --------------
@user_passes_test(is_vendedor)
def metodo_pago_list(request):
    query = request.GET.get('q', '').strip()
    selected_estado = request.GET.get('estado', '').strip()

    metodos = MetodoPago.objects.all().order_by('nombre')

    if query:
        metodos = metodos.filter(Q(nombre__icontains=query))

    if selected_estado == 'activo':
        metodos = metodos.filter(estado=True)
    elif selected_estado == 'inactivo':
        metodos = metodos.filter(estado=False)

    return render(request, 'metodo_pago_list.html', {
        'metodos': metodos,
        'query': query,
        'selected_estado': selected_estado,
    })


@user_passes_test(is_vendedor)
def metodo_pago_create(request):
    if request.method == 'POST':
        form = MetodoPagoForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Método de pago creado exitosamente.')
            return redirect('metodo_pago_list')
    else:
        form = MetodoPagoForm()

    return render(request, 'crud/form.html', {
        'form': form,
        'title': 'Crear Método de Pago',
        'cancel_url': 'metodo_pago_list',
    })


@user_passes_test(is_vendedor)
def metodo_pago_update(request, pk):
    metodo = get_object_or_404(MetodoPago, id_metodo_pago=pk)

    if request.method == 'POST':
        form = MetodoPagoForm(request.POST, instance=metodo)

        if form.is_valid():
            form.save()
            messages.success(request, 'Método de pago actualizado exitosamente.')
            return redirect('metodo_pago_list')
    else:
        form = MetodoPagoForm(instance=metodo)

    return render(request, 'crud/form.html', {
        'form': form,
        'title': 'Editar Método de Pago',
        'cancel_url': 'metodo_pago_list',
    })


@user_passes_test(is_vendedor)
def metodo_pago_delete(request, pk):
    metodo = get_object_or_404(MetodoPago, id_metodo_pago=pk)

    if request.method == 'POST':
        metodo.estado = False
        metodo.save(update_fields=['estado'])
        messages.success(request, 'Método de pago inactivado correctamente.')
        return redirect('metodo_pago_list')

    return render(request, 'crud/confirm_delete.html', {
        'obj': metodo,
        'title': 'Inactivar Método de Pago',
        'cancel_url': 'metodo_pago_list',
    })

# -------------- PROCESAMIENTO DE VENTA --------------

@transaction.atomic
def process_sale(request):
    """
    Procesa la venta final: valida stock, crea Venta y DetalleVenta,
    actualiza inventario y limpia el carrito.
    """
    if request.method != 'POST':
        return redirect('view_cart')

    form = CheckoutForm(request.POST)
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, 'El carrito está vacío.')
        return redirect('view_cart')

    if not form.is_valid():
        messages.error(request, 'Por favor corrige los errores del formulario.')
        return render(request, 'cart.html', _build_cart_context(request, form))

    metodo = form.cleaned_data['metodo_pago']
    nombre_cliente = form.cleaned_data['nombre_cliente']
    email_cliente = form.cleaned_data['email_cliente']
    tipo_venta = 'Presencial' if request.user.is_authenticated and request.user.rol in ['Administrador', 'Vendedor'] else 'Cotiza'

    venta = Venta.objects.create(
        empleado=request.user if request.user.is_authenticated else None,
        metodo_pago=metodo,
        nombre_cliente=nombre_cliente,
        email_cliente=email_cliente,
        tipo_venta=tipo_venta,
    )

    detalle_texto = ''
    total_venta = Decimal('0.00')
    productos_detalle = []

    for item_id, item_data in cart.items():
        producto = Producto.objects.select_for_update().get(id_producto=item_id)
        cantidad = int(item_data['quantity'])

        if producto.stock < cantidad:
            transaction.set_rollback(True)
            messages.error(request, f'Error: {producto.nombre} ya no tiene suficiente stock.')
            return redirect('view_cart')

        subtotal = producto.precio * cantidad
        total_venta += subtotal

        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            nombre_cliente=nombre_cliente,
            cantidad=cantidad,
            precio_unitario=producto.precio,
            subtotal=subtotal,
        )

        productos_detalle.append({
            'nombre': producto.nombre,
            'cantidad': cantidad,
            'precio': producto.precio,
            'subtotal': subtotal,
        })
        detalle_texto += f'• {producto.nombre}: {cantidad} x ${producto.precio} = ${subtotal}\n'

        producto.stock -= cantidad
        producto.save(update_fields=['stock'])

    try:
        subject = 'Compra Abaddon Store'
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="background-color: #111; color: white; padding: 20px; text-align: center;">¡Gracias por tu compra!</h2>
                <h3>Hola {nombre_cliente},</h3>
                <p>Gracias por elegir <strong>Abaddon Store</strong>. Este es el resumen de tu compra:</p>
        """
        for producto in productos_detalle:
            html_message += f"""
                <div style="padding: 10px; border-bottom: 1px solid #eee;">
                    <strong>{producto['nombre']}</strong><br>
                    Cantidad: {producto['cantidad']} x ${producto['precio']} = <strong>${producto['subtotal']}</strong>
                </div>
            """
        html_message += f"""
                <p><strong>Total a pagar: ${total_venta}</strong></p>
                <p><strong>Método de pago:</strong> {metodo.nombre}</p>
                <p><strong>Tipo de operación:</strong> {venta.get_tipo_venta_display()}</p>
                <p><strong>Fecha:</strong> {venta.fecha.strftime('%d/%m/%Y %H:%M')}</p>
                <p><em>El equipo de Abaddon Store</em></p>
            </div>
        </body>
        </html>
        """

        plain_message = f"""Hola {nombre_cliente},

Gracias por elegir Abaddon Store.

--- RESUMEN DE TU COMPRA ---
{detalle_texto}
TOTAL A PAGAR: ${total_venta}
MÉTODO DE PAGO: {metodo.nombre}
TIPO DE OPERACIÓN: {venta.get_tipo_venta_display()}
FECHA: {venta.fecha.strftime('%d/%m/%Y %H:%M')}

El equipo de Abaddon Store
"""

        send_mail(
            subject,
            plain_message,
            'abaddon.store01@gmail.com',
            [email_cliente],
            fail_silently=False,
            html_message=html_message,
        )
        messages.success(request, f'Venta procesada exitosamente. Se envió confirmación a {email_cliente}.')
    except Exception as exc:
        try:
            Auditoria.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                accion='ERROR_EMAIL',
                descripcion=f'Error al enviar correo a {email_cliente}: {exc}',
                tabla_afectada='VENTA',
            )
        except Exception:
            pass
        messages.warning(request, 'Venta procesada exitosamente, pero no se pudo enviar el correo de confirmación.')

    request.session['cart'] = {}
    return redirect('home')

