from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import Http404

# Dados de placeholder (nível do módulo para reuso)
_placeholder_all_products = [
    {'id': 1, 'nome': 'Bolo de Cenoura Delicioso', 'preco': '22.50', 'vendedor_nome': 'Doceria da Maria',
     'imagem_arquivo_local': 'bolo_de_cenoura.png', 'categoria_id': 'doces',
     'descricao_longa': 'Um delicioso e fofinho bolo de cenoura com cobertura de chocolate artesanal...'},
    {'id': 2, 'nome': 'Coxinha Crocante (Unidade)', 'preco': '7.00', 'vendedor_nome': 'Salgados Express',
     'imagem_arquivo_local': 'coxinha.png', 'categoria_id': 'salgados',
     'descricao_longa': 'Nossa famosa coxinha de frango com catupiry...'},
    {'id': 4, 'nome': 'PF Executivo - Frango Grelhado', 'preco': '28.00', 'vendedor_nome': 'Restaurante Sabor Caseiro',
     'imagem_arquivo_local': 'frango_grelhado.png', 'categoria_id': 'pratos_prontos',
     'descricao_longa': 'Prato feito completo com frango grelhado suculento...'},
    {'id': 5, 'nome': 'Brigadeiro Gourmet (Unidade)', 'preco': '4.50', 'vendedor_nome': 'Doceria da Maria',
     'imagem_arquivo_local': 'brigadeiro.png', 'categoria_id': 'doces',
     'descricao_longa': 'Brigadeiro gourmet feito com chocolate nobre...'},
    {'id': 6, 'nome': 'Mini Pizza Calabresa', 'preco': '8.00', 'vendedor_nome': 'Pizzaria Universitária',
     'imagem_arquivo_local': 'mini_pizza_calabresa.png', 'categoria_id': 'lanchinhos',
     'descricao_longa': 'Mini pizza individual com massa artesanal...'},
    {'id': 7, 'nome': 'Empada de Palmito', 'preco': '6.50', 'vendedor_nome': 'Salgados da Tia',
     'imagem_arquivo_local': 'empada_de_palmito.png', 'categoria_id': 'salgados',
     'descricao_longa': 'Delicada empada de palmito com massa que desmancha...'},
]

_filter_categorias_example = [
    {'id': 'pratos_prontos', 'nome_exibicao': 'Pratos Prontos', 'icone': '🍽️'},
    {'id': 'lanchinhos', 'nome_exibicao': 'Lanchinhos', 'icone': '🥪'},
    {'id': 'doces', 'nome_exibicao': 'Doces', 'icone': '🍰'},
    {'id': 'salgados', 'nome_exibicao': 'Salgados', 'icone': '🥐'},
]

# SIMULAÇÃO DA LISTA DE DESEJOS EM MEMÓRIA
_simulacao_ids_favoritados = [1, 4] # Ex: Produto 1 (Bolo) e 4 (PF) estão favoritados


# ========= VIEWS PÚBLICAS / DE ENTRADA =========
def landing_page(request):
    return render(request, 'comprador/inicial.html')

# ========= VIEWS DO ADMIN ==========
# (COLE AQUI TODAS AS SUAS FUNÇÕES DE VIEW DE ADMIN COMPLETAS: admin_login, admin_dashboard, etc.)
def admin_login(request): # Exemplo
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
# ... (Suas outras views de admin) ...
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request): return render(request, "admin/dashboard.html")
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_anuncios(request): return render(request, "admin/anuncios.html")
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_usuarios(request): return render(request, "admin/usuarios.html")
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_usuario(request): return render(request, "admin/gerenciar_usuario.html")
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reportes(request): return render(request, "admin/reportes.html")
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_reporte(request): return render(request, "admin/gerenciar_reporte.html")
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reportes_arquivados(request): return render(request, "admin/reportes_arquivados.html")
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_reporte_arquivado(request): return render(request, "admin/gerenciar_reporte_arquivado.html")
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_pedidos(request): return render(request, "admin/pedidos.html")
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_pedido(request): return render(request, "admin/gerenciar_pedido.html")
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_pedidos_finalizados(request): return render(request, "admin/pedidos_finalizados.html")
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_pedido_finalizado(request): return render(request, "admin/gerenciar_pedido_finalizado.html")
@login_required
def admin_logout(request): logout(request); return redirect('marketplace:login')


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
            user.first_name = nome; user.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso! Você já está logado.')
            return redirect('marketplace:pagina_inicial_comprador')
        except Exception as e:
            messages.error(request, 'Ocorreu um erro inesperado durante o cadastro.')
            return redirect('marketplace:comprador_cadastro')
    return render(request, 'comprador/cadastro.html')

def _enrich_products_with_favorite_status(product_list, favorite_ids):
    """Helper function to add 'is_favorited' status to products."""
    # Criar uma cópia profunda para não modificar a lista original _placeholder_all_products diretamente
    # se product_list for uma referência a ela ou uma fatia dela.
    # Se product_list já for uma nova lista (cópia), a cópia profunda pode não ser necessária.
    # Mas para ser seguro com listas de dicionários:
    import copy
    enriched_list = copy.deepcopy(product_list)
    for product in enriched_list:
        if product.get('id') in favorite_ids:
            product['is_favorited'] = True
        else:
            product['is_favorited'] = False
    return enriched_list

@login_required
def home_comprador(request):
    if request.user.is_staff:
        logout(request)
        messages.error(request, "Área restrita a compradores.")
        return redirect('marketplace:landing_page')
        
    nome_usuario = request.user.first_name or request.user.username
    selected_category_id = request.GET.get('categoria')
    search_query = request.GET.get('q_search', '').strip()

    product_list_to_display = list(_placeholder_all_products) 

    if selected_category_id and selected_category_id != 'todos':
        product_list_to_display = [p for p in product_list_to_display if p.get('categoria_id') == selected_category_id]
    
    if search_query:
        search_results = []
        for p in product_list_to_display:
            if (search_query.lower() in p.get('nome', '').lower() or
                search_query.lower() in p.get('descricao_longa', '').lower() or
                search_query.lower() in p.get('vendedor_nome', '').lower()):
                search_results.append(p)
        product_list_to_display = search_results
    
    # Adiciona status de favorito aos produtos
    product_list_to_display = _enrich_products_with_favorite_status(product_list_to_display, _simulacao_ids_favoritados)

    context = {
        'nome_usuario': nome_usuario,
        'filter_categorias': _filter_categorias_example,
        'product_list': product_list_to_display,
        'selected_category_id': selected_category_id,
        'search_query': search_query,
    }
    return render(request, 'comprador/home_comprador.html', context)

@login_required
def pagina_busca_produto(request):
    if request.user.is_staff:
        logout(request)
        messages.error(request, "Área restrita a compradores.")
        return redirect('marketplace:landing_page')
        
    nome_usuario = request.user.first_name or request.user.username
    selected_category_id = request.GET.get('categoria')
    search_query = request.GET.get('q_search', '').strip()
    current_product_list = []
    selected_category_name = None

    if selected_category_id and selected_category_id != 'todos':
        for cat in _filter_categorias_example:
            if cat['id'] == selected_category_id:
                selected_category_name = cat['nome_exibicao']
                break
    
    if search_query:
        current_product_list = list(_placeholder_all_products)
        if selected_category_id and selected_category_id != 'todos':
            current_product_list = [p for p in current_product_list if p.get('categoria_id') == selected_category_id]
        search_results = []
        for p in current_product_list:
            if (search_query.lower() in p.get('nome', '').lower() or
                search_query.lower() in p.get('descricao_longa', '').lower() or
                search_query.lower() in p.get('vendedor_nome', '').lower()):
                search_results.append(p)
        current_product_list = search_results
    elif selected_category_id and selected_category_id != 'todos':
        current_product_list = [p for p in _placeholder_all_products if p.get('categoria_id') == selected_category_id]
    
    # Adiciona status de favorito aos produtos da busca
    current_product_list = _enrich_products_with_favorite_status(current_product_list, _simulacao_ids_favoritados)
    
    context = {
        'nome_usuario': nome_usuario,
        'filter_categorias': _filter_categorias_example,
        'product_list': current_product_list,
        'search_query': search_query,
        'selected_category_id': selected_category_id,
        'selected_category_name': selected_category_name,
    }
    return render(request, 'comprador/pagina_busca_produto.html', context)

@login_required
def detalhes_produto(request, produto_id):
    produto_encontrado_original = None
    for p in _placeholder_all_products: 
        if p.get('id') == produto_id:
            produto_encontrado_original = p
            break
    if not produto_encontrado_original:
        raise Http404("Produto não encontrado.")

    # Adiciona status de favorito ao produto
    # Crie uma cópia para não modificar a lista global _placeholder_all_products
    import copy
    produto_encontrado = copy.deepcopy(produto_encontrado_original)
    produto_encontrado['is_favorited'] = produto_encontrado.get('id') in _simulacao_ids_favoritados
    
    context = {
        'produto': produto_encontrado,
        'nome_usuario': request.user.first_name or request.user.username if request.user.is_authenticated else None,
    }
    return render(request, 'comprador/detalhes_produto.html', context)

# --- VIEWS PARA LISTA DE DESEJOS (SIMULADAS) ---
@login_required
def adicionar_aos_desejos(request, produto_id):
    global _simulacao_ids_favoritados
    produto_id = int(produto_id)
    if produto_id not in _simulacao_ids_favoritados:
        _simulacao_ids_favoritados.append(produto_id)
        messages.success(request, "Produto adicionado à sua lista de desejos!")
    else:
        messages.info(request, "Este produto já está na sua lista de desejos.")
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:lista_desejos'))

@login_required
def remover_dos_desejos(request, produto_id):
    global _simulacao_ids_favoritados
    produto_id = int(produto_id)
    if produto_id in _simulacao_ids_favoritados:
        _simulacao_ids_favoritados.remove(produto_id)
        messages.success(request, "Produto removido da sua lista de desejos!")
    else:
        messages.info(request, "Este produto não estava na sua lista de desejos.")
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:lista_desejos'))

@login_required
def lista_desejos(request):
    if request.user.is_staff:
        logout(request)
        messages.error(request, "Página não disponível para administradores.")
        return redirect('marketplace:landing_page')
        
    nome_usuario = request.user.first_name or request.user.username
    
    produtos_favoritados_list = [p for p in _placeholder_all_products if p.get('id') in _simulacao_ids_favoritados]
    # Adiciona status de favorito (todos serão True aqui)
    produtos_favoritados_list = _enrich_products_with_favorite_status(produtos_favoritados_list, _simulacao_ids_favoritados)

    context = {
        'nome_usuario': nome_usuario,
        'produtos_favoritados': produtos_favoritados_list,
    }
    return render(request, 'comprador/lista_desejos.html', context)
# --- FIM DAS VIEWS PARA LISTA DE DESEJOS ---

@login_required
def comprador_logout(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('marketplace:landing_page')