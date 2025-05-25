from django.urls import path
from . import views

app_name = 'marketplace'  # Define um namespace para as URLs deste app

urlpatterns = [
    # URL para a Landing Page (página pública inicial)
    # Esta será a página em "seusite.com/" se este urls.py for incluído com path('', ...) no urls.py do projeto


    # URLs do Admin (mantendo sua estrutura original)
    path('admin/', views.admin_login, name='login'), # Nota: Nome 'login' é genérico. Poderia ser 'admin_login'.
    path('admin/dashboard/', views.admin_dashboard, name='dashboard'),
    path('admin/anuncios/', views.admin_anuncios, name='anuncios'),
    path('admin/usuarios/', views.admin_usuarios, name='usuarios'),
    path('admin/gerenciar_usuario/', views.admin_gerenciar_usuario, name='gerenciar_usuario'),
    path('admin/reportes/', views.admin_reportes, name='reportes'),
    path('admin/gerenciar_reporte/', views.admin_gerenciar_reporte, name='gerenciar_reporte'),
    path('admin/reportes_arquivados/', views.admin_reportes_arquivados, name='reportes_arquivados'),
    path('admin/gerenciar_reporte_arquivado/', views.admin_gerenciar_reporte_arquivado, name='gerenciar_reporte_arquivado'),
    path('admin/pedidos/', views.admin_pedidos, name='pedidos'),
    path('admin/gerenciar_pedidos/', views.admin_gerenciar_pedido, name='gerenciar_pedidos'), # 'gerenciar_pedidos' é um bom nome
    path('admin/pedidos_finalizados/', views.admin_pedidos_finalizados, name='pedidos_finalizados'),
    path('admin/gerenciar_pedido_finalizado/', views.admin_gerenciar_pedido_finalizado, name='gerenciar_pedido_finalizado'),
    path('admin/logout/', views.admin_logout, name='admin_logout'), # Renomeado para 'admin_logout' para clareza

    # URLs do Comprador
    path('', views.landing_page, name='landing_page'),

    path('comprador/login/', views.comprador_login, name='comprador_login'),
    path('comprador/cadastro/', views.comprador_cadastro, name='comprador_cadastro'),
    
    path('comprador/home/', views.comprador_inicial, name='pagina_inicial_comprador'),
    path('comprador/logout/', views.comprador_logout, name='comprador_logout'),
]