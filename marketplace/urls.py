from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'marketplace'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('admin/', views.admin_login, name='login'),
    path('admin/dashboard/', views.admin_dashboard, name='dashboard'),
    path('admin/anuncios/', views.admin_anuncios, name='anuncios'),
    path('admin/usuarios/', views.admin_usuarios, name='usuarios'),
    path('admin/gerenciar_usuario/', views.admin_gerenciar_usuario, name='gerenciar_usuario'),
    path('admin/reportes/', views.admin_reportes, name='reportes'),
    path('admin/gerenciar_reporte/', views.admin_gerenciar_reporte, name='gerenciar_reporte'),
    path('admin/reportes_arquivados/', views.admin_reportes_arquivados, name='reportes_arquivados'),
    path('admin/gerenciar_reporte_arquivado/', views.admin_gerenciar_reporte_arquivado, name='gerenciar_reporte_arquivado'),
    path('admin/pedidos/', views.admin_pedidos, name='pedidos'),
    path('admin/gerenciar_pedidos/', views.admin_gerenciar_pedido, name='gerenciar_pedidos'),
    path('admin/pedidos_finalizados/', views.admin_pedidos_finalizados, name='pedidos_finalizados'),
    path('admin/gerenciar_pedido_finalizado/', views.admin_gerenciar_pedido_finalizado, name='gerenciar_pedido_finalizado'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),

    path('comprador/login/', views.comprador_login, name='comprador_login'),
    path('comprador/cadastro/', views.comprador_cadastro, name='comprador_cadastro'),
    path('comprador/home/', views.home_comprador, name='pagina_inicial_comprador'),
    path('comprador/logout/', views.comprador_logout, name='comprador_logout'),
    path('comprador/produto/<int:produto_id>/', views.detalhes_produto, name='detalhes_produto'),
    path('comprador/busca/', views.pagina_busca_produto, name='pagina_busca_produto'),

    path('comprador/esqueceu-senha/',
         auth_views.PasswordResetView.as_view(
             template_name='comprador/esquece_senha.html',
             email_template_name='comprador/esquece_senha_email_corpo.html',
             subject_template_name='comprador/esquece_senha_email_assunto.txt',
             success_url=reverse_lazy('marketplace:password_reset_done'),
             extra_email_context={'app_name': app_name}
         ),
         name='password_reset_request'),
    path('comprador/esqueceu-senha/email-enviado/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='comprador/esquece_senha_email_enviado.html'
         ),
         name='password_reset_done'),
    path('comprador/resetar-senha/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='comprador/esquece_senha_nova_senha_form.html',
             success_url=reverse_lazy('marketplace:password_reset_complete')
         ),
         name='password_reset_confirm'),
    path('comprador/resetar-senha/concluido/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='comprador/esquece_senha_completo.html'
         ),
         name='password_reset_complete'),
]