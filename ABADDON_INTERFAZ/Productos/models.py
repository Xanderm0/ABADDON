from cloudinary.models import CloudinaryField
from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator
from decimal import Decimal

# Create your models here.
class Categoria(models.Model):
    """
    Representa las categorías de los productos (ej. Camisetas, Pantalones).
    """
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=15, validators=[MinLengthValidator(3)])
    descripcion = models.TextField(null=True, blank=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'CATEGORIA'

    def __str__(self):
        return self.nombre_categoria

class Producto(models.Model):
    """
    Representa un artículo a la venta en la tienda.
    """
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=35, validators=[MinLengthValidator(3)])
    descripcion = models.TextField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0, validators=[MinValueValidator(Decimal('0.01'))])
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='id_categoria')
    imagen = CloudinaryField(
    'imagen',
    folder='abaddon/productos',
    null=True,
    blank=True
)
    estado = models.BooleanField(default=True) # Disponible para la venta

    class Meta:
        db_table = 'PRODUCTO'

    def __str__(self):
        return self.nombre