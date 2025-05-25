from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

# ========= VIEWS PÚBLICAS / DE ENTRADA =========

def landing_page(request):
    """
    Renderiza a página inicial pública do site.
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
            return redirect('marketplace:dashboard') # ATUALIZADO com namespace
        else:
            messages.error(request, 'Credenciais inválidas ou você não tem permissão para acessar o admin.')
            return redirect('marketplace:login') # ATUALIZADO com namespace (assumindo 'login' é o name da url admin_login)
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

@login_required
def admin_logout(request):
    logout(request)
    return redirect('marketplace:login') # ATUALIZADO com namespace (assumindo 'login' é o name da url admin_login)

# ========================
# VIEWS DO COMPRADOR
# ========================

def comprador_login(request):
    if request.user.is_authenticated and not request.user.is_staff: # Se já logado como comprador
        return redirect('marketplace:pagina_inicial_comprador') # ATUALIZADO

    if request.method == 'POST':
        email = request.POST.get('username') # Usando 'username' como no seu HTML
        senha = request.POST.get('password') # Usando 'password' como no seu HTML
        user = authenticate(request, username=email, password=senha)
        if user is not None:
            if not user.is_staff: # Garante que não é um admin tentando logar aqui
                login(request, user)
                return redirect('marketplace:pagina_inicial_comprador') # ATUALIZADO
            else:
                messages.error(request, 'Conta de administrador. Use o login de admin.')
                return redirect('marketplace:comprador_login') # ATUALIZADO
        else:
            messages.error(request, 'Email ou senha inválidos.')
            return redirect('marketplace:comprador_login') # ATUALIZADO
    return render(request, 'comprador/login.html')


def comprador_cadastro(request): # FUNÇÃO COMPLETA E ATUALIZADA
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('marketplace:pagina_inicial_comprador')

    if request.method == 'POST':
        nome = request.POST.get('nome')
        idade = request.POST.get('idade')
        cpf = request.POST.get('cpf')
        curso = request.POST.get('curso')
        ra = request.POST.get('ra')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # Validação básica para todos os campos
        if not all([nome, idade, cpf, curso, ra, email, senha, confirmar_senha]):
            messages.error(request, 'Todos os campos são obrigatórios.')
            return redirect('marketplace:comprador_cadastro')

        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('marketplace:comprador_cadastro')

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, 'Já existe um usuário com este email.')
            return redirect('marketplace:comprador_cadastro')
        
        try:
            idade_int = int(idade)
            if idade_int < 16: # Exemplo de idade mínima
                messages.error(request, 'Você precisa ter pelo menos 16 anos para se cadastrar.')
                return redirect('marketplace:comprador_cadastro')
        except ValueError:
            messages.error(request, 'Idade inválida. Por favor, insira um número.')
            return redirect('marketplace:comprador_cadastro')
        
        # Adicionar aqui validações mais robustas para CPF (formato, validade), RA, etc.

        try:
            user = User.objects.create_user(username=email, email=email, password=senha)
            user.first_name = nome
            user.save()

            # LÓGICA PARA SALVAR OS DADOS EXTRAS (idade, cpf, curso, ra)
            # Isso dependerá de como seu colega estruturou o banco de dados.
            # Exemplo: se houver um modelo UserProfile ligado ao User:
            # from .models import UserProfile # Supondo que UserProfile está em models.py
            # UserProfile.objects.create(
            #     user=user,
            #     idade=idade_int,
            #     cpf=cpf, # Idealmente, limpe e valide o CPF antes de salvar
            #     curso=curso,
            #     ra=ra
            # )
            # print(f"Dados recebidos: Idade={idade_int}, CPF={cpf}, Curso={curso}, RA={ra}. Lógica de salvamento pendente.")


            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso! Você já está logado.')
            return redirect('marketplace:pagina_inicial_comprador')
        except Exception as e:
            # Em um ambiente de produção, registre o erro 'e' em logs, não o mostre ao usuário.
            messages.error(request, 'Ocorreu um erro inesperado durante o cadastro. Tente novamente.')
            # print(f"Erro no cadastro: {e}") # Para debug no terminal
            return redirect('marketplace:comprador_cadastro')
            
    return render(request, 'comprador/cadastro.html')


@login_required
def comprador_inicial(request): # Home do comprador logado
    # Evitar que admin acesse a home do comprador e vice-versa
    if request.user.is_staff:
        logout(request) # Faz logout do admin se ele tentar acessar aqui
        messages.error(request, "Área restrita a compradores.")
        return redirect('marketplace:landing_page') # ou 'marketplace:login_comprador'
        
    # No futuro, esta view renderizará um template diferente (ex: 'comprador/home.html')
    # e passará dados específicos do comprador.
    return render(request, 'comprador/inicial.html') 


@login_required
def comprador_logout(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('marketplace:landing_page')