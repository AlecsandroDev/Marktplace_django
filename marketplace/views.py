from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

# ========= VIEWS PÚBLICAS / DE ENTRADA =========

def landing_page(request): # MANTENHA ESTA landing_page
    """
    Renderiza a página inicial pública do site (o design do Figma).
    Esta página não requer login.
    """
    return render(request, 'comprador/inicial.html')

# ========================
# VIEWS DO ADMIN
# ========================

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            # ATUALIZE ESTE REDIRECT se 'dashboard' estiver em marketplace/urls.py
            return redirect('marketplace:dashboard')
        else:
            messages.error(request, 'Credenciais inválidas ou você não tem permissão para acessar o admin.')
            # ATUALIZE ESTE REDIRECT se 'login' for o name do admin_login em marketplace/urls.py
            return redirect('marketplace:login')
    return render(request, "admin/login.html")


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    return render(request, "admin/dashboard.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_anuncios(request):
    return render(request, "admin/anuncios.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_usuarios(request):
    return render(request, "admin/usuarios.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_usuario(request):
    return render(request, "admin/gerenciar_usuario.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reportes(request):
    return render(request, "admin/reportes.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_reporte(request):
    return render(request, "admin/gerenciar_reporte.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reportes_arquivados(request):
    return render(request, "admin/reportes_arquivados.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_reporte_arquivado(request):
    return render(request, "admin/gerenciar_reporte_arquivado.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_pedidos(request):
    return render(request, "admin/pedidos.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_pedido(request):
    return render(request, "admin/gerenciar_pedido.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_pedidos_finalizados(request):
    return render(request, "admin/pedidos_finalizados.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_pedido_finalizado(request):
    return render(request, "admin/gerenciar_pedido_finalizado.html")

@login_required # Geralmente, o logout do admin não precisa ser restrito a admin logado, mas ok.
def admin_logout(request):
    logout(request)
    # ATUALIZE ESTE REDIRECT se 'login' for o name do admin_login em marketplace/urls.py
    return redirect('marketplace:login')


# ========================
# VIEWS DO COMPRADOR
# ========================

def comprador_login(request):
    if request.user.is_authenticated:
        # ATUALIZE ESTE REDIRECT
        return redirect('marketplace:pagina_inicial_comprador')

    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        user = authenticate(request, username=email, password=senha)
        if user is not None:
            login(request, user)
            # ATUALIZE ESTE REDIRECT
            return redirect('marketplace:pagina_inicial_comprador')
        else:
            messages.error(request, 'Email ou senha inválidos.')
            # ATUALIZE ESTE REDIRECT
            return redirect('marketplace:comprador_login')
    return render(request, 'comprador/login.html')


def comprador_cadastro(request):
    if request.user.is_authenticated:
        # ATUALIZE ESTE REDIRECT
        return redirect('marketplace:pagina_inicial_comprador')

    if request.method == 'POST':
        # ... (lógica de validação e criação do usuário) ...
        # Dentro do try, após login(request, user):
        if 'user' in locals() and user.is_authenticated: # Garante que user existe e foi logado
             # ATUALIZE ESTE REDIRECT
            return redirect('marketplace:pagina_inicial_comprador')
        # Nos blocos de erro (messages.error):
        # ATUALIZE ESTES REDIRECTS
        # return redirect('marketplace:comprador_cadastro')
    return render(request, 'comprador/cadastro.html') # Ver Ponto 2 abaixo

@login_required
def comprador_inicial(request):
    return render(request, 'comprador/inicial.html') # Temporário. Idealmente, um novo HTML para home logada.

@login_required
def comprador_logout(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    # ESTE JÁ ESTÁ CORRETO se você adicionou app_name='marketplace'
    return redirect('marketplace:landing_page')