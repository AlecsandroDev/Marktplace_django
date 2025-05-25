from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
# Se for usar os modelos de Produto e Categoria na view home_comprador, importe-os aqui quando estiverem prontos:
# from .models import Produto, Categoria # Exemplo

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
            return redirect('marketplace:dashboard')
        else:
            messages.error(request, 'Credenciais inválidas ou você não tem permissão para acessar o admin.')
            return redirect('marketplace:login') # 'login' aqui é o name da URL do admin_login
    return render(request, "admin/login.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    return render(request, "admin/dashboard.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_anuncios(request): # ADICIONADA DE VOLTA
    return render(request, "admin/anuncios.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_usuarios(request): # ADICIONADA DE VOLTA
    return render(request, "admin/usuarios.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_usuario(request): # ADICIONADA DE VOLTA
    return render(request, "admin/gerenciar_usuario.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reportes(request): # ADICIONADA DE VOLTA
    return render(request, "admin/reportes.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_reporte(request): # ADICIONADA DE VOLTA
    return render(request, "admin/gerenciar_reporte.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reportes_arquivados(request): # ADICIONADA DE VOLTA
    return render(request, "admin/reportes_arquivados.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_reporte_arquivado(request): # ADICIONADA DE VOLTA
    return render(request, "admin/gerenciar_reporte_arquivado.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_pedidos(request): # ADICIONADA DE VOLTA
    return render(request, "admin/pedidos.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_pedido(request): # ADICIONADA DE VOLTA
    return render(request, "admin/gerenciar_pedido.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_pedidos_finalizados(request): # ADICIONADA DE VOLTA
    return render(request, "admin/pedidos_finalizados.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_pedido_finalizado(request): # ADICIONADA DE VOLTA
    return render(request, "admin/gerenciar_pedido_finalizado.html")

@login_required
def admin_logout(request):
    logout(request)
    return redirect('marketplace:login') # 'login' aqui é o name da URL do admin_login

# ========================
# VIEWS DO COMPRADOR
# ========================

def comprador_login(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('marketplace:pagina_inicial_comprador')

    if request.method == 'POST':
        email = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=email, password=senha)
        if user is not None:
            if not user.is_staff:
                login(request, user)
                return redirect('marketplace:pagina_inicial_comprador')
            else:
                messages.error(request, 'Conta de administrador. Use o login de admin.')
                return redirect('marketplace:comprador_login')
        else:
            messages.error(request, 'Email ou senha inválidos.')
            return redirect('marketplace:comprador_login')
    return render(request, 'comprador/login.html')


def comprador_cadastro(request):
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
            if idade_int < 16:
                messages.error(request, 'Você precisa ter pelo menos 16 anos para se cadastrar.')
                return redirect('marketplace:comprador_cadastro')
        except ValueError:
            messages.error(request, 'Idade inválida. Por favor, insira um número.')
            return redirect('marketplace:comprador_cadastro')
        
        try:
            user = User.objects.create_user(username=email, email=email, password=senha)
            user.first_name = nome
            user.save()
            
            # Lógica para salvar dados extras (idade, cpf, etc.) em um UserProfile aqui
            # print(f"Dados recebidos: Idade={idade_int}, CPF={cpf}, Curso={curso}, RA={ra}. Lógica de salvamento pendente.")

            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso! Você já está logado.')
            return redirect('marketplace:pagina_inicial_comprador')
        except Exception as e:
            messages.error(request, 'Ocorreu um erro inesperado durante o cadastro. Tente novamente.')
            return redirect('marketplace:comprador_cadastro')
            
    return render(request, 'comprador/cadastro.html')

@login_required
def home_comprador(request): # Esta é a nova home do comprador logado
    if request.user.is_staff:
        logout(request)
        messages.error(request, "Área restrita a compradores.")
        return redirect('marketplace:landing_page')
        
    nome_usuario = request.user.first_name or request.user.username
    
    filter_categorias = [
        {'id': 'pratos_prontos', 'nome_exibicao': 'Pratos Prontos', 'icone': '🍽️'},
        {'id': 'lanchinhos', 'nome_exibicao': 'Lanchinhos', 'icone': '🥪'},
        {'id': 'doces', 'nome_exibicao': 'Doces', 'icone': '🍰'},
        {'id': 'salgados', 'nome_exibicao': 'Salgados', 'icone': '🥐'},
    ]

    product_list = [
        {'id': 1, 'nome': 'Bolo de Cenoura Delicioso', 'preco': '22.50', 'vendedor_nome': 'Doceria da Maria', 'imagem_url': 'https://via.placeholder.com/300x200/FFDAB9/000000?text=Bolo+Cenoura'},
        {'id': 2, 'nome': 'Coxinha Crocante (Unidade)', 'preco': '7.00', 'vendedor_nome': 'Salgados Express', 'imagem_url': 'https://via.placeholder.com/300x200/FFDEAD/000000?text=Coxinha'},
        # ... (mais produtos de exemplo se desejar)
    ]
    
    context = {
        'nome_usuario': nome_usuario,
        'filter_categorias': filter_categorias,
        'product_list': product_list,
    }
    return render(request, 'comprador/home_comprador.html', context)

@login_required
def comprador_logout(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('marketplace:landing_page')