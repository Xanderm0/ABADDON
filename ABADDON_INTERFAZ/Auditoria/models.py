from django.db import models
from Usuarios.models import Usuario

class Auditoria(models.Model):
    """
    Sistema de logs para rastrear cambios importantes en las tablas del sistema.
    """
    id_auditoria = models.AutoField(primary_key=True)
    tabla_afectada = models.CharField(max_length=20)
    accion = models.CharField(max_length=20) # ej. INSERT, UPDATE, DELETE
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, db_column='id_usuario')
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()

    class Meta:
        db_table = 'AUDITORIA'