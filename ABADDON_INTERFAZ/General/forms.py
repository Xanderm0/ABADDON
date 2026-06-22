from django import forms
from Usuarios.models import Usuario
from Productos.models import Producto, Categoria
from Ventas.models import MetodoPago, Venta
from .models import letras_validator
import re

class CheckoutForm(forms.Form):
    """
    Formulario para capturar los datos del cliente durante la compra online/presencial.
    No está ligado a un modelo directamente para permitir compras rápidas.
    """
    nombre_cliente = forms.CharField(
        max_length=50, 
        validators=[letras_validator],
        label="Nombre Completo",
        widget=forms.TextInput(attrs={'placeholder': 'Ej: Juan Pérez'})
    )
    email_cliente = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'})
    )
    metodo_pago = forms.ModelChoiceField(
        queryset=MetodoPago.objects.filter(estado=True),
        label="Método de Pago",
        empty_label="Seleccione un método..."
    )

class UsuarioForm(forms.ModelForm):
    """
    Formulario para la gestión de usuarios (empleados/admins).
    Incluye validaciones de seguridad para la contraseña.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 8 caracteres, 1 Mayúscula, 1 Número'}), 
        min_length=8,
        label="Contraseña",
        required=False # Es opcional en actualizaciones para no obligar a cambiarla
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita la contraseña'}),
        label="Confirmar Contraseña",
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'rol', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Juan Pérez'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'}),
        }
        labels = {
            'nombre': 'Nombre Completo',
            'email': 'Correo Electrónico',
            'rol': 'Rol de Usuario',
            'estado': 'Cuenta Activa'
        }

    def clean_password(self):
        """Valida que la contraseña cumpla con requisitos mínimos de seguridad."""
        password = self.cleaned_data.get('password')
        if password:
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError("La contraseña debe incluir al menos una letra mayúscula.")
            if not re.search(r'[0-9]', password):
                raise forms.ValidationError("La contraseña debe incluir al menos un número.")
        return password

    def clean(self):
        """Verifica que ambas contraseñas coincidan."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

class ProductoForm(forms.ModelForm):
    """Formulario para la creación y edición de productos con placeholders informativos."""
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'imagen', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Camiseta Gótica'}),
            'descripcion': forms.Textarea(attrs={'placeholder': 'Detalles del producto...', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'placeholder': '0.00'}),
            'stock': forms.NumberInput(attrs={'placeholder': 'Cantidad disponible'}),
        }
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'precio': 'Precio ($)',
            'stock': 'Stock Disponible',
            'categoria': 'Categoría',
            'imagen': 'Imagen del Producto',
            'estado': 'Disponible para la Venta'
        }

class VentaForm(forms.ModelForm):
    """Formulario simplificado para editar cabeceras de venta ya realizadas."""
    class Meta:
        model = Venta
        fields = ['metodo_pago', 'estado', 'nombre_cliente', 'email_cliente']
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={'placeholder': 'Nombre del cliente'}),
            'email_cliente': forms.EmailInput(attrs={'placeholder': 'correo@cliente.com'}),
        }
        labels = {
            'metodo_pago': 'Método de Pago',
            'estado': 'Venta Completada/Activa',
            'nombre_cliente': 'Nombre del Cliente',
            'email_cliente': 'Correo del Cliente'
        }

class MetodoPagoForm(forms.ModelForm):
    """Formulario para gestionar los métodos de pago habilitados."""
    class Meta:
        model = MetodoPago
        fields = ['nombre', 'estado']
        labels = {
            'nombre': 'Nombre del Método',
            'estado': 'Habilitado'
        }

class CategoriaForm(forms.ModelForm):
    """Formulario para la gestión de categorías de productos."""
    class Meta:
        model = Categoria
        fields = ['nombre_categoria', 'descripcion', 'estado']
        widgets = {
            'nombre_categoria': forms.TextInput(attrs={'placeholder': 'Ej: Camisetas, Accesorios'}),
            'descripcion': forms.Textarea(attrs={'placeholder': 'Breve descripción de la categoría...', 'rows': 3}),
        }
        labels = {
            'nombre_categoria': 'Nombre de la Categoría',
            'descripcion': 'Descripción',
            'estado': 'Habilitada'
        }

