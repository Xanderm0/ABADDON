import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ABADDON.settings')
django.setup()

from Productos.models import Categoria, Producto


def populate():
    # Categorías
    joyeria, _ = Categoria.objects.get_or_create(
        nombre_categoria='Joyería',
        defaults={'descripcion': 'Anillos, collares y más'}
    )

    ropa, _ = Categoria.objects.get_or_create(
        nombre_categoria='Ropa',
        defaults={'descripcion': 'Vestimenta gótica y urbana'}
    )

    instrumentos, _ = Categoria.objects.get_or_create(
        nombre_categoria='Instrumentos',
        defaults={'descripcion': 'Guitarras, bajos y accesorios'}
    )

    accesorios, _ = Categoria.objects.get_or_create(
        nombre_categoria='Accesorios',
        defaults={'descripcion': 'Cinturones, parches y otros'}
    )

    # Productos en pesos colombianos COP
    items_joyeria = [
        ('Anillo Calavera Plata', 180000),
        ('Collar Cuervo Gótico', 140000),
        ('Pulsera de Cuero y Pinchos', 95000),
        ('Pendientes de Pentagrama', 70000),
        ('Gargantilla de Terciopelo', 85000),
        ('Anillo de Sello Negro', 120000),
        ('Collar de Cruz Invertida', 110000),
        ('Brazalete de Dragón', 220000),
        ('Anillo de Garra', 80000),
        ('Tiara de Cristal Negro', 300000),
    ]

    items_ropa = [
        ('Chaqueta de Cuero Negra', 480000),
        ('Camiseta Calavera Art', 95000),
        ('Pantalones Cargo Negros', 260000),
        ('Corset de Encaje', 340000),
        ('Capa de Terciopelo', 440000),
        ('Botas de Plataforma', 560000),
        ('Sudadera Oversize Dark', 220000),
        ('Falda de Tul Negra', 180000),
        ('Guantes de Rejilla', 60000),
        ('Gabardina Larga', 720000),
    ]

    items_instrumentos = [
        ('Guitarra Eléctrica Abyss', 1800000),
        ('Bajo Eléctrico Nocturno', 2080000),
        ('Pedal de Distorsión Brutal', 380000),
        ('Correa de Guitarra con Calaveras', 120000),
        ('Set de Cuerdas de Acero', 60000),
        ('Amplificador 20W Dark', 480000),
        ('Funda Acolchada para Bajo', 160000),
        ('Púas Personalizadas (Pack 10)', 40000),
        ('Cable Blindado 3m', 80000),
        ('Soporte de Guitarra Vertical', 100000),
    ]

    items_accesorios = [
        ('Cinturón de Balas', 180000),
        ('Parche Bordado Abaddon', 30000),
        ('Mochila de Cuero Sintético', 280000),
        ('Gafas de Sol Steampunk', 140000),
        ('Máscara de Gas Decorativa', 240000),
        ('Cartera con Cadena', 95000),
        ('Sombrero de Copa Gótico', 200000),
        ('Pañuelo de Calaveras', 45000),
        ('Pin Metálico Cuervo', 25000),
        ('Llavero de Ataúd', 35000),
    ]

    all_items = [
        (items_joyeria, joyeria),
        (items_ropa, ropa),
        (items_instrumentos, instrumentos),
        (items_accesorios, accesorios),
    ]

    count = 0

    for item_list, category in all_items:
        for nombre, precio in item_list:
            Producto.objects.update_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': f"Descripción profesional para {nombre}. Calidad garantizada en Abaddon.",
                    'precio': Decimal(str(precio)),
                    'stock': random.randint(5, 50),
                    'categoria': category,
                    'estado': True,
                }
            )
            count += 1

    print(f"Base de datos poblada o actualizada con {count} productos en pesos colombianos.")


if __name__ == '__main__':
    populate()