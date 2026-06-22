from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from General.forms import CategoriaForm, ProductoForm
from General.views import is_vendedor, is_admin, is_admin_vendedor
from .models import Categoria, Producto

from django.db import transaction
import csv
import json

# --- CATÁLOGO DE PRODUCTOS ---

def catalogo(request):
    """Alias del catálogo público."""
    return filtro_cat(request)


def filtro_cat(request):
    """Muestra el catálogo público con búsqueda y filtro por categoría."""
    query = request.GET.get('q', '').strip()
    cat_id = request.GET.get('categoria', '').strip()

    productos = Producto.objects.select_related('categoria').filter(estado=True, categoria__estado=True).order_by('nombre')

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query)
            | Q(descripcion__icontains=query)
            | Q(nombre__istartswith=query)
        )

    if cat_id:
        productos = productos.filter(categoria_id=cat_id)

    categorias = Categoria.objects.filter(estado=True).order_by('nombre_categoria')

    return render(request, 'catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'selected_cat': cat_id,
    })

# --- GESTIÓN DE PRODUCTOS ---

@user_passes_test(is_admin_vendedor)
def producto_admin_list(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip().lower()
    categoria = request.GET.get('categoria', '').strip()

    precio_min = request.GET.get('precio_min', '').strip()
    precio_max = request.GET.get('precio_max', '').strip()
    stock_min = request.GET.get('stock_min', '').strip()
    stock_max = request.GET.get('stock_max', '').strip()

    productos = Producto.objects.select_related('categoria').all().order_by('nombre')
    categorias = Categoria.objects.all().order_by('nombre_categoria')

    if q:
        productos = productos.filter(
            Q(nombre__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(categoria__nombre_categoria__icontains=q)
        )

    if categoria:
        productos = productos.filter(categoria_id=categoria)

    if estado == 'activo':
        productos = productos.filter(estado=True)
    elif estado == 'inactivo':
        productos = productos.filter(estado=False)

    if precio_min:
        try:
            productos = productos.filter(precio__gte=Decimal(precio_min))
        except InvalidOperation:
            pass

    if precio_max:
        try:
            productos = productos.filter(precio__lte=Decimal(precio_max))
        except InvalidOperation:
            pass

    if stock_min:
        try:
            productos = productos.filter(stock__gte=int(stock_min))
        except ValueError:
            pass

    if stock_max:
        try:
            productos = productos.filter(stock__lte=int(stock_max))
        except ValueError:
            pass
    
    if estado == 'activo':
        productos = productos.filter(estado=True)
    elif estado == 'inactivo':
        productos = productos.filter(estado=False)

    return render(request, 'producto_admin_list.html', {
        'productos': productos,
        'categorias': categorias,
    })


@user_passes_test(is_vendedor)
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('producto_admin_list')
    else:
        form = ProductoForm()

    return render(request, 'crud/form.html', {
        'form': form,
        'title': 'Crear Producto',
        'cancel_url': 'producto_admin_list'
    })


@user_passes_test(is_vendedor)
def producto_update(request, pk):
    """Vista para editar un producto existente."""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('producto_admin_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'crud/form.html', {'form': form, 'title': 'Editar Producto'})


@user_passes_test(is_vendedor)
def producto_delete(request, pk):
    """Inactiva un producto sin borrar su historial."""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.estado = False
        producto.save(update_fields=['estado'])
        messages.success(request, 'Producto inactivado correctamente.')
        return redirect('producto_admin_list')
    return render(request, 'crud/confirm_delete.html', {
        'obj': producto,
        'title': 'Inactivar Producto',
        'cancel_url': 'producto_admin_list',
    })


# --- GESTIÓN DE CATEGORÍAS ---

@user_passes_test(is_vendedor)
def categoria_list(request):
    """Lista categorías con búsqueda y filtro por estado."""
    query = request.GET.get('q', '').strip()
    selected_estado = request.GET.get('estado', '').strip()

    categorias = Categoria.objects.all().order_by('nombre_categoria')

    if query:
        categorias = categorias.filter(
            Q(nombre_categoria__icontains=query)
        )

    if selected_estado == 'activo':
        categorias = categorias.filter(estado=True)
    elif selected_estado == 'inactivo':
        categorias = categorias.filter(estado=False)

    return render(request, 'categoria_list.html', {
        'categorias': categorias,
        'query': query,
        'selected_estado': selected_estado,
    })


@user_passes_test(is_vendedor)
def categoria_create(request):
    """Crea una nueva categoría."""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('categoria_list')
    else:
        form = CategoriaForm()
    return render(request, 'crud/form.html', {'form': form, 'title': 'Crear Categoría'})


@user_passes_test(is_vendedor)
def categoria_update(request, pk):
    """Edita una categoría existente."""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada.')
            return redirect('categoria_list')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'crud/form.html', {'form': form, 'title': 'Editar Categoría'})


@user_passes_test(is_vendedor)
def categoria_delete(request, pk):
    """Inactiva una categoría sin borrar sus productos ni reportes."""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.estado = False
        categoria.save(update_fields=['estado'])
        messages.success(request, 'Categoría inactivada correctamente.')
        return redirect('categoria_list')
    return render(request, 'crud/confirm_delete.html', {
        'obj': categoria,
        'title': 'Inactivar Categoría',
        'cancel_url': 'categoria_list',
    })

# --- CARGA MASIVA DE PRODUCTOS ---
@user_passes_test(is_admin)
def bulk_upload(request):
    """
    Permite subir archivos CSV o JSON para cargar productos masivamente.
    Crea automáticamente las categorías si no existen.
    """
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        filename = file.name.lower()

        # Como esta vista es para productos, lo dejamos fijo.
        model_type = request.POST.get('model_type', 'productos')

        try:
            if filename.endswith('.json'):
                data = json.load(file)

                if isinstance(data, dict):
                    if model_type in data:
                        data = data[model_type]
                    elif 'data' in data:
                        data = data['data']
                    else:
                        data = [data]

            elif filename.endswith('.csv'):
                decoded_file = file.read().decode('utf-8-sig').splitlines()
                data = list(csv.DictReader(decoded_file))

            else:
                messages.error(request, "Formato no soportado. Usa archivos .csv o .json.")
                return redirect('carga_masiva')

            if not isinstance(data, list):
                messages.error(request, "El archivo debe contener una lista de productos.")
                return redirect('carga_masiva')

            count = 0

            with transaction.atomic():
                if model_type == 'productos':
                    for item in data:
                        cat_id = item.get('id_categoria')
                        cat_name = item.get('nombre_categoria')

                        if cat_id:
                            categoria = Categoria.objects.get(id_categoria=cat_id)
                        elif cat_name:
                            categoria, _ = Categoria.objects.get_or_create(
                                nombre_categoria=cat_name,
                                defaults={
                                    'descripcion': '',
                                    'estado': True
                                }
                            )
                        else:
                            raise ValueError("Cada producto requiere id_categoria o nombre_categoria.")

                        Producto.objects.create(
                            nombre=item['nombre'],
                            descripcion=item.get('descripcion', ''),
                            precio=Decimal(str(item['precio'])),
                            stock=int(item['stock']),
                            categoria=categoria,
                            estado=str(item.get('estado', 'True')).lower() == 'true'
                        )

                        count += 1

                else:
                    messages.error(request, "Tipo de carga no válido.")
                    return redirect('carga_masiva')

            messages.success(request, f"Se cargaron {count} registros exitosamente.")
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f"Error en la carga: {e}")
            return redirect('carga_masiva')

    return render(request, 'bulk_upload.html')