from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseForbidden
from django.db import transaction
from django.db.models import Q
from .models import Perfil, Categoria, Anuncio, ItemListaDesejos, Avaliacao, Pedido, Reporte, Cep

# Dados de placeholder (nível do módulo para reuso) - Luan: removido pois dados virão do Banco de Dados
# _placeholder_all_products removido
# _filter_categorias_example removido
# __simulacao_ids_favoritados removido

# SIMULAÇÃO DA LISTA DE DESEJOS EM MEMÓRIA - Luan: removido pois dados virão do Banco de Dados
# __simulacao_ids_favoritados removido
# Ex: Produto 1 (Bolo) e 4 (PF) estão favoritados

# ========= FUNÇÕES PARA USO POSTERIOR =========
def is_comprador(user):
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.tipo == 'comprador'

def is_vendedor(user): # Se você for usar esta também
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.tipo == 'vendedor'

def staff_user_check(user): # Para proteger views de admin
    return user.is_staff

# ========= VIEWS PÚBLICAS / DE ENTRADA =========
def landing_page(request):
    if is_comprador(request.user):
        return redirect('marketplace:pagina_inicial_comprador')
    return render(request, 'comprador/inicial.html')
# LUAN - CONTINUAR DAQUI

# ========= VIEWS DO ADMIN ==========   
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff: # Verifica se é staff
            login(request, user)
            return redirect('marketplace:admin_dashboard') # CORRETO: Redireciona após login
        else:
            messages.error(request, 'Credenciais inválidas ou você não tem permissão para acessar o admin.')
            return redirect('marketplace:admin_login') # CORRETO: Redireciona para a página de login em caso de erro

    # CORRETO: Renderiza o template da página de login para requisições GET
    return render(request, "admin/login.html")


# View para exibir o dashboard do administrador
@login_required # Garante que o usuário esteja logado
@user_passes_test(lambda u: u.is_staff) # Garante que o usuário seja staff
def admin_dashboard(request):
    # ALTERADO: Renderiza o template do dashboard em vez de redirecionar
    # Supondo que seu template seja 'admin/dashboard.html'
    # Ajuste o nome/caminho do template se necessário.
    return render(request, 'admin/dashboard.html') 

# As views abaixo são para exibir páginas, então render() está CORRETO.

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_anuncios(request):
    # Adicione aqui o contexto necessário para o template, se houver
    # context = {'anuncios': Anuncio.objects.all()}
    # return render(request, "admin/anuncios.html", context)
    return render(request, "admin/anuncios.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_usuarios(request):
    return render(request, "admin/usuarios.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_usuario(request):
    # Geralmente, uma view "gerenciar_X" pode receber um ID para gerenciar um item específico
    # ou pode ser uma página com um formulário para criar/editar.
    # Se receber um ID, você o pegaria aqui (ex: request.GET.get('id') ou da URL).
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

# View para processar o logout do administrador
@login_required # Garante que apenas usuários logados possam tentar deslogar
def admin_logout(request):
    logout(request)
    return redirect('marketplace:admin_login') # CORRETO: Redireciona para a página de login após logout


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
def adicionar_aos_desejos(request, produto_id): # produto_id refere-se a Anuncio.id
    if not is_comprador(request.user): # Usando o helper definido anteriormente
        # Pode retornar um erro, ou redirecionar, ou mostrar mensagem
        messages.error(request, "Apenas compradores podem adicionar itens à lista de desejos.")
        return redirect(request.META.get('HTTP_REFERER', 'marketplace:pagina_inicial_comprador'))

    anuncio = get_object_or_404(Anuncio, pk=produto_id)
    item, created = ItemListaDesejos.objects.get_or_create(usuario=request.user, anuncio=anuncio)
    
    if created:
        messages.success(request, f"'{anuncio.titulo}' foi adicionado à sua lista de desejos!")
    else:
        messages.info(request, f"'{anuncio.titulo}' já estava na sua lista de desejos.")
    
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:lista_desejos'))

@login_required
def remover_dos_desejos(request, produto_id): # produto_id refere-se a Anuncio.id
    if not is_comprador(request.user):
        messages.error(request, "Apenas compradores podem remover itens da lista de desejos.")
        return redirect(request.META.get('HTTP_REFERER', 'marketplace:pagina_inicial_comprador'))

    anuncio = get_object_or_404(Anuncio, pk=produto_id)
    try:
        item = ItemListaDesejos.objects.get(usuario=request.user, anuncio=anuncio)
        item.delete()
        messages.success(request, f"'{anuncio.titulo}' foi removido da sua lista de desejos.")
    except ItemListaDesejos.DoesNotExist:
        messages.info(request, f"'{anuncio.titulo}' não estava na sua lista de desejos.")
        
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:lista_desejos'))

@login_required
def lista_desejos(request):
    if not is_comprador(request.user):
        logout(request) # Se um admin ou outro tipo de usuário acessar, desloga.
        messages.error(request, "Página não disponível para este tipo de usuário.")
        return redirect('marketplace:comprador_login')
        
    nome_usuario = request.user.first_name or request.user.username
    
    # Busca os itens da lista de desejos e os anúncios relacionados
    itens_desejados = ItemListaDesejos.objects.filter(usuario=request.user).select_related('anuncio', 'anuncio__usuario', 'anuncio__categoria').order_by('-data_adicao')
    
    # Prepara a lista de anúncios para o template, similar ao home_comprador
    anuncios_favoritados_display = []
    for item in itens_desejados:
        anuncios_favoritados_display.append({
            'obj': item.anuncio,
            'is_favorited': True # Todos aqui são favoritados por definição
        })

    context = {
        'nome_usuario': nome_usuario,
        'anuncios_favoritados_display': anuncios_favoritados_display, # Passa a lista processada
    }
    return render(request, 'comprador/lista_desejos.html', context)
# --- FIM DAS VIEWS PARA LISTA DE DESEJOS ---

@login_required
def comprador_logout(request):
    # Verifica se o usuário logado é um comprador antes de fazer logout desta URL específica
    # Isso é opcional, pois @login_required já garante que há um usuário.
    # if not is_comprador(request.user):
    #     messages.warning(request, "Você não estava logado como comprador.")
    #     # Pode redirecionar para uma página de logout genérica ou landing page
    #     logout(request)
    #     return redirect('marketplace:landing_page')

    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('marketplace:landing_page') # Redireciona para a landing page principal