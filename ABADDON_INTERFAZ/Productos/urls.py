from django.urls import path

from . import views

urlpatterns = [
    # Catálogo público
    path('', views.filtro_cat, name='producto_list'),
    path('catalogo/', views.catalogo, name='catalogo'),

    # Gestión administrativa
    path('gestion/', views.producto_admin_list, name='producto_admin_list'),
    path('gestion/crear/', views.producto_create, name='producto_create'),
    path('gestion/editar/<int:pk>/', views.producto_update, name='producto_update'),
    path('gestion/eliminar/<int:pk>/', views.producto_delete, name='producto_delete'),

    # Categorías
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/crear/', views.categoria_create, name='categoria_create'),
    path('categorias/editar/<int:pk>/', views.categoria_update, name='categoria_update'),
    path('categorias/eliminar/<int:pk>/', views.categoria_delete, name='categoria_delete'),

    # Carga Masiva
    path('bulk-upload/', views.bulk_upload, name='carga_masiva'), # Carga masiva de archivos
]