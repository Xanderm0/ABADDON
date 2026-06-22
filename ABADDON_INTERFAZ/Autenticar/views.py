from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from Usuarios.models import Usuario


def login_view(request):
    """Maneja el inicio de sesión de empleados y administradores."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        try:
            user_obj = Usuario.objects.get(email=email)
            if not user_obj.is_active or not user_obj.estado:
                messages.error(request, 'Su usuario está inactivo. Comuníquese con el administrador o jefe a cargo.')
                return render(request, 'login.html')
        except Usuario.DoesNotExist:
            pass

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Credenciales inválidas.')

    return render(request, 'login.html')


def logout_view(request):
    """Cierra la sesión del usuario."""
    logout(request)
    return redirect('home')
