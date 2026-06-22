from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('nombre', 'email', 'rol', 'estado', 'is_staff')
    search_fields = ('nombre', 'email')
    list_filter = ('rol', 'estado', 'is_staff', 'is_superuser')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('nombre', 'rol', 'estado')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'fecha_creacion')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'rol', 'password1', 'password2', 'is_staff', 'is_superuser', 'estado'),
        }),
    )
    readonly_fields = ('fecha_creacion', 'last_login')
