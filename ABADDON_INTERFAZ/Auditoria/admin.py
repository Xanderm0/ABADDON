from django.contrib import admin

from .models import Auditoria


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('tabla_afectada', 'accion', 'usuario', 'fecha')
    search_fields = ('tabla_afectada', 'accion', 'descripcion')
    list_filter = ('tabla_afectada', 'accion', 'fecha')
