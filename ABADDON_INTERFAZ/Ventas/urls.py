from django.urls import path

from . import views

urlpatterns = [
    # Ventas
    path('', views.venta_list, name='venta_list'),
    path('editar/<int:pk>/', views.venta_update, name='venta_update'),
    path('anular/<int:pk>/', views.venta_delete, name='venta_anular'),
    path('eliminar/<int:pk>/', views.venta_delete, name='venta_delete'),  # Compatibilidad con enlaces antiguos: también anula.
    path('eliminar-definitivo/<int:pk>/', views.venta_delete_permanent, name='venta_delete_real'),
    path('detalle_venta/<int:pk>', views.detalle_venta, name="detalle_venta"),

    # Carrito
    path('carrito/', views.view_cart, name='view_cart'),
    path('carrito/agregar/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/actualizar/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('carrito/eliminar/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('carrito/procesar/', views.process_sale, name='process_sale'),

    # Método de Pago
    path('metodos_pago/', views.metodo_pago_list, name='metodo_pago_list'),
    path('metodos_pago/crear/', views.metodo_pago_create, name='metodo_pago_create'),
    path('metodos_pago/editar/<int:pk>/', views.metodo_pago_update, name='metodo_pago_update'),
    path('metodos_pago/eliminar/<int:pk>/', views.metodo_pago_delete, name='metodo_pago_delete'),
]
