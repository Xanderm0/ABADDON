from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404, redirect, render

from General.forms import UsuarioForm
from General.views import is_admin
from Usuarios.models import Usuario
from django.db.models import Q

@user_passes_test(is_admin)
def usuario_list(request):
    query = request.GET.get('q', '').strip()
    selected_estado = request.GET.get('estado', '').strip()
    selected_rol = request.GET.get('rol', '').strip()

    usuarios = Usuario.objects.all().order_by('nombre')

    if query:
        usuarios = usuarios.filter(
            Q(nombre__icontains=query) |
            Q(email__icontains=query) |
            Q(rol__icontains=query)
        )

    if selected_estado == 'activo':
        usuarios = usuarios.filter(estado=True)
    elif selected_estado == 'inactivo':
        usuarios = usuarios.filter(estado=False)
    
    if selected_rol:
        usuarios = usuarios.filter(rol__iexact=selected_rol)

    return render(request, 'usuario_list.html', {
        'usuarios': usuarios,
        'query': query,
        'selected_rol': selected_rol,
        'selected_estado': selected_estado,
    })


@user_passes_test(is_admin)
def usuario_create(request):
    """Crea un nuevo usuario con contraseña cifrada."""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.is_active = user.estado
            user.save()
            messages.success(request, 'Usuario creado.')
            return redirect('usuario_list')
    else:
        form = UsuarioForm()
    return render(request, 'crud/form.html', {'form': form, 'title': 'Crear Usuario'})


@login_required
def usuario_update(request, pk):
    """Actualiza datos del usuario y permite cambio opcional de contraseña."""
    usuario = get_object_or_404(Usuario, pk=pk)
    is_admin_actual = request.user.rol.lower() == 'administrador'

    if not is_admin_actual and usuario.pk != request.user.pk:
        messages.error(request, 'No tienes permisos para editar este usuario.')
        return redirect('dashboard')

    campos_bloqueados = [] if is_admin_actual else ['rol', 'estado', 'is_staff', 'is_superuser']

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        for campo in campos_bloqueados:
            if campo in form.fields:
                form.fields.pop(campo)

        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.is_active = user.estado
            user.save()
            messages.success(request, 'Usuario actualizado.')

            if is_admin_actual:
                return redirect('usuario_list')
            return redirect('dashboard')
    else:
        form = UsuarioForm(instance=usuario)
        for campo in campos_bloqueados:
            if campo in form.fields:
                form.fields.pop(campo)

    return render(request, 'crud/form.html', {
        'form': form,
        'title': 'Editar Usuario',
        'cancel_url': 'usuario_list' if is_admin_actual else 'dashboard',
    })


@user_passes_test(is_admin)
def usuario_delete(request, pk):
    """Inactiva un usuario sin eliminar su historial."""
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.estado = False
        usuario.is_active = False
        usuario.save(update_fields=['estado', 'is_active'])
        messages.success(request, 'Usuario inactivado correctamente.')
        return redirect('usuario_list')
    return render(request, 'crud/confirm_delete.html', {
        'obj': usuario,
        'title': 'Inactivar Usuario',
        'cancel_url': 'usuario_list',
    })
