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
    return redirect('marketplace:login')

# ========================
# VIEWS DO COMPRADOR
# ========================

def comprador_login(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('marketplace:pagina_inicial_comprador')

    if request.method == 'POST':
        # ... (lógica de login que você já tem e está funcionando) ...
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
        # ... (lógica de cadastro que você já tem e está funcionando com todos os campos) ...
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
def home_comprador(request):
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

    all_products = [
        {'id': 1, 'nome': 'Bolo de Cenoura Delicioso', 'preco': '22.50', 'vendedor_nome': 'Doceria da Maria', 
         'imagem_arquivo_local': 'bolo_de_cenoura.png', 'categoria_id': 'doces'},
        {'id': 2, 'nome': 'Coxinha Crocante (Unidade)', 'preco': '7.00', 'vendedor_nome': 'Salgados Express',
         'imagem_arquivo_local': 'coxinha.png', 'categoria_id': 'salgados'},
        {'id': 4, 'nome': 'PF Executivo - Frango Grelhado', 'preco': '28.00', 'vendedor_nome': 'Restaurante Sabor Caseiro', 
         'imagem_arquivo_local': 'frango_grelhado.png', 'categoria_id': 'pratos_prontos'},
        {'id': 5, 'nome': 'Brigadeiro Gourmet (Unidade)', 'preco': '4.50', 'vendedor_nome': 'Doceria da Maria', 
         'imagem_arquivo_local': 'brigadeiro.png', 'categoria_id': 'doces'},
        {'id': 6, 'nome': 'Mini Pizza Calabresa', 'preco': '8.00', 'vendedor_nome': 'Pizzaria Universitária',
         'imagem_arquivo_local': 'mini_pizza_calabresa.png', 'categoria_id': 'lanchinhos'},  
        {'id': 7, 'nome': 'Empada de Palmito', 'preco': '6.50', 'vendedor_nome': 'Salgados da Tia',
         'imagem_arquivo_local': 'empada_de_palmito.png', 'categoria_id': 'salgados'},     
    ]

    selected_category_id = request.GET.get('categoria')
    product_list = all_products

    if selected_category_id and selected_category_id != 'todos': # Adicionado 'todos' como condição para não filtrar
        product_list = [p for p in all_products if p.get('categoria_id') == selected_category_id]
    
    context = {
        'nome_usuario': nome_usuario,
        'filter_categorias': filter_categorias,
        'product_list': product_list,
        'selected_category_id': selected_category_id,
    }
    return render(request, 'comprador/home_comprador.html', context)

@login_required
def comprador_logout(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('marketplace:landing_page')