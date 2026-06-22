from django.urls import path, include

from . import views
from Autenticar import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('productos/', include('Productos.urls')),
    path('usuarios/', include('Usuarios.urls')),
    path('ventas/', include('Ventas.urls')),

    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('reportes/', include('Reportes.urls')),
]
