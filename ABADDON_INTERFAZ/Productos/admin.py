from django.contrib import admin

from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre_categoria', 'estado')
    search_fields = ('nombre_categoria',)
    list_filter = ('estado',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'estado')
    search_fields = ('nombre',)
    list_filter = ('categoria', 'estado')
