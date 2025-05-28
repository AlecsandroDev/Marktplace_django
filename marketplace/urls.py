from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'marketplace'

urlpatterns = [
    # ... (todas as suas URLs existentes: landing_page, admin, comprador_login, etc.) ...
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
    
    path('comprador/lista-desejos/', views.lista_desejos, name='lista_desejos'),
    path('comprador/desejos/adicionar/<int:produto_id>/', views.adicionar_aos_desejos, name='adicionar_aos_desejos'),
    path('comprador/desejos/remover/<int:produto_id>/', views.remover_dos_desejos, name='remover_dos_desejos'),

    path('comprador/carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('comprador/carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('comprador/carrinho/remover/<int:item_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    
    path('comprador/perfil/', views.perfil_comprador, name='perfil_comprador'),
    path('comprador/perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('comprador/perfil/encerrar-conta/', views.encerrar_conta, name='encerrar_conta'),

    path('comprador/perfil/alterar-senha/', 
         auth_views.PasswordChangeView.as_view(
             template_name='comprador/perfil_alterar_senha_form.html',
             success_url=reverse_lazy('marketplace:password_change_done')
         ), 
         name='password_change'),
    path('comprador/perfil/alterar-senha/concluido/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='comprador/perfil_alterar_senha_concluido.html'
         ), 
         name='password_change_done'),

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

    path('comprador/meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('comprador/meus-pedidos/<int:pedido_id>/', views.detalhe_pedido, name='detalhe_pedido'),
    path('comprador/pedir-novamente/<int:pedido_id>/', views.pedir_novamente, name='pedir_novamente'),
    path('comprador/pedido/<int:pedido_id>/avaliar-item/<int:produto_id>/', views.submeter_avaliacao_pedido, name='submeter_avaliacao_pedido'),

    path('comprador/checkout/', views.checkout_pagina, name='checkout'),
    path('comprador/pedido-confirmado/<int:pedido_id_simulado>/', views.pedido_confirmado, name='pedido_confirmado'),
]