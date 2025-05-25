from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import Http404

# Se for usar os modelos de Produto e Categoria, importe-os aqui quando estiverem prontos:
# from .models import Produto, Categoria # Exemplo


# Dados de placeholder para produtos (nível do módulo)
_placeholder_all_products = [
    {'id': 1, 'nome': 'Bolo de Cenoura Delicioso', 'preco': '22.50', 'vendedor_nome': 'Doceria da Maria',
     'imagem_arquivo_local': 'bolo_de_cenoura.png', 'categoria_id': 'doces',
     'descricao_longa': 'Um delicioso e fofinho bolo de cenoura com cobertura de chocolate artesanal, feito com ingredientes frescos e muito carinho. Perfeito para o seu café da tarde ou como sobremesa especial.'},
    {'id': 2, 'nome': 'Coxinha Crocante (Unidade)', 'preco': '7.00', 'vendedor_nome': 'Salgados Express',
     'imagem_arquivo_local': 'coxinha.png', 'categoria_id': 'salgados',
     'descricao_longa': 'Nossa famosa coxinha de frango com catupiry, com massa crocante por fora e recheio cremoso e abundante por dentro. Frita na hora para você!'},
    {'id': 4, 'nome': 'PF Executivo - Frango Grelhado', 'preco': '28.00', 'vendedor_nome': 'Restaurante Sabor Caseiro',
     'imagem_arquivo_local': 'frango_grelhado.png', 'categoria_id': 'pratos_prontos',
     'descricao_longa': 'Prato feito completo com frango grelhado suculento, arroz branco soltinho, feijão caseiro, batata frita crocante e uma salada fresca de alface e tomate.'},
    {'id': 5, 'nome': 'Brigadeiro Gourmet (Unidade)', 'preco': '4.50', 'vendedor_nome': 'Doceria da Maria',
     'imagem_arquivo_local': 'brigadeiro.png', 'categoria_id': 'doces',
     'descricao_longa': 'Brigadeiro gourmet feito com chocolate nobre e granulado de alta qualidade. Uma explosão de sabor que derrete na boca.'},
    {'id': 6, 'nome': 'Mini Pizza Calabresa', 'preco': '8.00', 'vendedor_nome': 'Pizzaria Universitária',
     'imagem_arquivo_local': 'mini_pizza_calabresa.png', 'categoria_id': 'lanchinhos',
     'descricao_longa': 'Mini pizza individual com massa artesanal, molho de tomate fresco, calabresa fatiada de primeira e queijo mussarela derretido. Ideal para um lanche rápido!'},
    {'id': 7, 'nome': 'Empada de Palmito', 'preco': '6.50', 'vendedor_nome': 'Salgados da Tia',
     'imagem_arquivo_local': 'empada_de_palmito.png', 'categoria_id': 'salgados',
     'descricao_longa': 'Delicada empada de palmito com massa que desmancha na boca e recheio cremoso. Uma ótima opção para qualquer hora do dia.'},
]

# ========= VIEWS PÚBLICAS / DE ENTRADA =========
def landing_page(request):
    return render(request, 'comprador/inicial.html')

# ========= VIEWS DO ADMIN ==========
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

    selected_category_id = request.GET.get('categoria')
    product_list = _placeholder_all_products # Usa a lista definida no início do arquivo

    if selected_category_id and selected_category_id != 'todos':
        product_list = [p for p in _placeholder_all_products if p.get('categoria_id') == selected_category_id]
    
    context = {
        'nome_usuario': nome_usuario,
        'filter_categorias': filter_categorias,
        'product_list': product_list,
        'selected_category_id': selected_category_id,
    }
    return render(request, 'comprador/home_comprador.html', context)

# NOVA VIEW PARA DETALHES DO PRODUTO
@login_required # Mantenha ou remova @login_required conforme sua necessidade para esta página
def detalhes_produto(request, produto_id):
    produto_encontrado = None
    for p in _placeholder_all_products: # Procura na lista de exemplo
        if p.get('id') == produto_id:
            produto_encontrado = p
            break
    
    if not produto_encontrado:
        # Quando tiver modelos, use:
        # from .models import Produto
        # produto_encontrado = get_object_or_404(Produto, pk=produto_id, disponivel=True)
        raise Http404("Produto não encontrado ou indisponível.")

    # Aqui você pode adicionar lógica para buscar produtos relacionados, avaliações, etc.
    # produtos_relacionados = [prod for prod in _placeholder_all_products if prod.get('categoria_id') == produto_encontrado.get('categoria_id') and prod.get('id') != produto_id][:3] # Exemplo

    context = {
        'produto': produto_encontrado,
        'nome_usuario': request.user.first_name or request.user.username if request.user.is_authenticated else None,
        # 'produtos_relacionados': produtos_relacionados, # Exemplo
    }
    return render(request, 'comprador/detalhes_produto.html', context)

@login_required
def comprador_logout(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('marketplace:landing_page')