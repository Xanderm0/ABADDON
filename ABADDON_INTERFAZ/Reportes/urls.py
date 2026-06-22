from django.urls import path
from . import views

urlpatterns = [
    path('', views.reportes, name='reportes'),

    path('pdf/<str:model_name>/', views.export_pdf_table, name='export_pdf_table'),
    path('reporte/pdf/', views.export_pdf_filtrado, name='export_pdf_filtrado'),
    path('ventas-detalle/pdf/', views.export_pdf_ventas_detalle, name='export_pdf_ventas_detalle'),
    path('general/pdf/', views.export_pdf_general, name='export_pdf_general'),
]