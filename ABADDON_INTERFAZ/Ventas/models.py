from django.db import models
from General.models import letras_validator
from Productos.models import Producto
from Usuarios.models import Usuario
from django.core.validators import MinValueValidator

class MetodoPago(models.Model):
    """
    Define los métodos de pago disponibles (ej. Efectivo, Tarjeta, Transferencia).
    """
    id_metodo_pago = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'METODO_PAGO'

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    """
    Cabecera de una transacción de venta. Registra quién vendió y a quién.
    """
    id_venta = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(auto_now_add=True)
    # Si es venta presencial, registra al empleado. Si es online, puede ser nulo.
    empleado = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_empleado', null=True, blank=True)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.CASCADE, db_column='id_metodo_pago')
    TIPO_VENTA = (
        ('Online', 'Venta Online'),
        ('Cotiza', 'Cotización Online'),
        ('Presencial', 'Venta en Tienda'),
    )
    nombre_cliente = models.CharField(max_length=50, validators=[letras_validator], default='Consumidor Final')
    email_cliente = models.EmailField(default='noreply@abaddon.com')
    tipo_venta = models.CharField(max_length=20, choices=TIPO_VENTA, default='Cotiza')
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'VENTA'

class DetalleVenta(models.Model):
    """
    Detalle de los productos incluidos en una venta específica.
    Permite mantener el historial de precios aunque el producto cambie de precio después.
    """
    id_detalle = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, db_column='id_venta', related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')
    nombre_cliente = models.CharField(max_length=20)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'DETALLE_VENTA'

