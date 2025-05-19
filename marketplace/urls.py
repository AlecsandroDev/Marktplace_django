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
    path('admin/pedidos', views.admin_pedidos, name='pedidos'),
    path('admin/gerenciar_pedidos', views.admin_gerenciar_pedido, name='gerenciar_pedidos'),
    path('admin/pedidos_finalizados', views.admin_pedidos_finalizados, name='pedidos_finalizados'),
    path('admin/gerenciar_pedido_finalizado', views.admin_gerenciar_pedido_finalizado, name='gerenciar_pedido_finalizado'),
    path('admin/logout', views.admin_logout, name='logout'),
]
