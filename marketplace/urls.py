from django.urls import path
from . import views

urlpatterns = [
    path('admin', views.admin_login, name='login'),
    path('admin/dashboard', views.admin_dashboard, name='dashboard'),
    path('admin/anuncios', views.admin_anuncios, name='anuncios'),
    path('admin/usuarios', views.admin_usuarios, name='usuarios'),
    path('admin/gerenciar_usuario', views.admin_gerenciar_usuario, name='gerenciar_usuario'),
    path('admin/reportes', views.admin_reportes, name='reportes'),
    path('admin/gerenciar_reporte', views.admin_gerenciar_reporte, name='gerenciar_reporte'),
    path('admin/reportes_arquivados', views.admin_reportes_arquivados, name='reportes_arquivados'),
    path('admin/gerenciar_reporte_arquivado', views.admin_gerenciar_reporte_arquivado, name='gerenciar_reporte_arquivado'),
    path('admin/logout', views.admin_logout, name='logout'),
]
