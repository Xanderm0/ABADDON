from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from General.models import letras_validator

class UsuarioManager(BaseUserManager):
    """
    Manager personalizado para el modelo Usuario que maneja la creación de usuarios
    normales y superusuarios utilizando el email como identificador único.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'Administrador')
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de Usuario personalizado que reemplaza el modelo por defecto de Django.
    Utiliza el email para el inicio de sesión.
    """
    ROLES = (
        ('Administrador', 'Administrador'),
        ('Vendedor', 'Vendedor'),
    )
    email = models.EmailField(unique=True, max_length=50)
    nombre = models.CharField(max_length=50, validators=[letras_validator])
    rol = models.CharField(max_length=20, choices=ROLES, default='Vendedor')
    estado = models.BooleanField(default=True) # Activo o Inactivo
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'USUARIO'

    def __str__(self):
        return f"{self.nombre} ({self.rol})"
