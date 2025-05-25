from django.urls import path, reverse_lazy # Adicione reverse_lazy
from . import views
from django.contrib.auth import views as auth_views # Importe as views de autenticação do Django

app_name = 'marketplace'

urlpatterns = [
    # URL para a Landing Page (página pública inicial)
    path('', views.landing_page, name='landing_page'),

    # URLs do Admin
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

    # URLs do Comprador
    path('comprador/login/', views.comprador_login, name='comprador_login'),
    path('comprador/cadastro/', views.comprador_cadastro, name='comprador_cadastro'),
    path('comprador/home/', views.home_comprador, name='pagina_inicial_comprador'),
    path('comprador/logout/', views.comprador_logout, name='comprador_logout'),

    # --- URLs para Recuperação de Senha do Comprador ---
    path('comprador/esqueceu-senha/',
         auth_views.PasswordResetView.as_view(
             template_name='comprador/esquece_senha.html', # SEU ARQUIVO
             email_template_name='comprador/esquece_senha_email_corpo.html', # Template para o corpo do email
             subject_template_name='comprador/esquece_senha_email_assunto.txt', # Template para o assunto do email
             success_url=reverse_lazy('marketplace:password_reset_done'), # Para onde ir após submeter o email
             extra_email_context={'app_name': app_name} # Passa o app_name para o template do email
         ),
         name='password_reset_request'), # Nome para o link "Esqueci minha senha"

    path('comprador/esqueceu-senha/email-enviado/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='comprador/esquece_senha_email_enviado.html' # Página de "email enviado"
         ),
         name='password_reset_done'),

    # Esta URL recebe uidb64 e token do email
    path('comprador/resetar-senha/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='comprador/esquece_senha_nova_senha_form.html', # Formulário para nova senha
             success_url=reverse_lazy('marketplace:password_reset_complete')
         ),
         name='password_reset_confirm'),

    path('comprador/resetar-senha/concluido/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='comprador/esquece_senha_completo.html' # Página de "senha redefinida"
         ),
         name='password_reset_complete'),
]