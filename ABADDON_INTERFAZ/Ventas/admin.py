from django.contrib import admin

from .models import MetodoPago, DetalleVenta, Venta

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado')
    search_fields = ('nombre',)
    list_filter = ('estado',)

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id_venta', 'nombre_cliente', 'email_cliente', 'tipo_venta', 'metodo_pago', 'fecha', 'estado')
    search_fields = ('nombre_cliente', 'email_cliente')
    list_filter = ('tipo_venta', 'estado', 'metodo_pago')
    inlines = [DetalleVentaInline]


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('nombre_cliente', 'producto__nombre')
