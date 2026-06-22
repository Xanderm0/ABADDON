from django.core.validators import RegexValidator

letras_validator = RegexValidator(
    regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
    message='Solo se permiten letras y espacios.'
)