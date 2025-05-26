from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import Http404
import copy # Para deepcopy

# --- Dados de Placeholder (nível do módulo para reuso) ---
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

_filter_categorias_example = [
    {'id': 'pratos_prontos', 'nome_exibicao': 'Pratos Prontos', 'icone': '🍽️'},
    {'id': 'lanchinhos', 'nome_exibicao': 'Lanchinhos', 'icone': '🥪'},
    {'id': 'doces', 'nome_exibicao': 'Doces', 'icone': '🍰'},
    {'id': 'salgados', 'nome_exibicao': 'Salgados', 'icone': '🥐'},
]

_simulacao_ids_favoritados = [1, 4] # Ex: Produtos com ID 1 e 4 estão favoritados

def _update_cart_item_count(request):
    """Atualiza a contagem de itens distintos no carrinho na sessão."""
    carrinho = request.session.get('carrinho', {})
    request.session['num_itens_carrinho'] = len(carrinho)
    request.session.modified = True

def _enrich_product_data(product_list_original, request_session, user_favorites_ids):
    """Adiciona status 'is_favorited' e 'is_in_cart' a uma lista de produtos."""
    enriched_list = copy.deepcopy(product_list_original)
    carrinho_session = request_session.get('carrinho', {})
    for product in enriched_list:
        product_id_str = str(product.get('id'))
        product['is_favorited'] = product.get('id') in user_favorites_ids
        product['is_in_cart'] = product_id_str in carrinho_session
    return enriched_list

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
                _update_cart_item_count(request) 
                next_url = request.GET.get('next')
                if next_url: return redirect(next_url)
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
        nome = request.POST.get('nome'); idade = request.POST.get('idade'); cpf = request.POST.get('cpf')
        curso = request.POST.get('curso'); ra = request.POST.get('ra'); email = request.POST.get('email')
        senha = request.POST.get('senha'); confirmar_senha = request.POST.get('confirmar_senha')

        if not all([nome, idade, cpf, curso, ra, email, senha, confirmar_senha]):
            messages.error(request, 'Todos os campos são obrigatórios.'); return redirect('marketplace:comprador_cadastro')
        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.'); return redirect('marketplace:comprador_cadastro')
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, 'Já existe um usuário com este email.'); return redirect('marketplace:comprador_cadastro')
        try:
            idade_int = int(idade)
            if idade_int < 16: messages.error(request, 'Você precisa ter pelo menos 16 anos.'); return redirect('marketplace:comprador_cadastro')
        except ValueError: messages.error(request, 'Idade inválida.'); return redirect('marketplace:comprador_cadastro')
        try:
            user = User.objects.create_user(username=email, email=email, password=senha)
            user.first_name = nome; user.save(); 
            login(request, user)
            _update_cart_item_count(request)
            messages.success(request, 'Cadastro realizado com sucesso! Você já está logado.')
            return redirect('marketplace:pagina_inicial_comprador')
        except Exception as e:
            messages.error(request, 'Ocorreu um erro inesperado durante o cadastro.'); return redirect('marketplace:comprador_cadastro')
    return render(request, 'comprador/cadastro.html')

@login_required
def home_comprador(request):
    if request.user.is_staff:
        logout(request); messages.error(request, "Área restrita a compradores."); return redirect('marketplace:landing_page')
        
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
    product_list_to_display = _enrich_product_data(product_list_to_display, request.session, _simulacao_ids_favoritados)
    context = {
        'nome_usuario': nome_usuario, 'filter_categorias': _filter_categorias_example,
        'product_list': product_list_to_display, 'selected_category_id': selected_category_id,
        'search_query': search_query,
    }
    return render(request, 'comprador/home_comprador.html', context)

@login_required
def pagina_busca_produto(request):
    if request.user.is_staff:
        logout(request); messages.error(request, "Área restrita a compradores."); return redirect('marketplace:landing_page')
    nome_usuario = request.user.first_name or request.user.username
    selected_category_id = request.GET.get('categoria')
    search_query = request.GET.get('q_search', '').strip()
    current_product_list = []; selected_category_name = None
    if selected_category_id and selected_category_id != 'todos':
        for cat in _filter_categorias_example:
            if cat['id'] == selected_category_id: selected_category_name = cat['nome_exibicao']; break
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
    
    current_product_list = _enrich_product_data(current_product_list, request.session, _simulacao_ids_favoritados)
    context = {
        'nome_usuario': nome_usuario, 'filter_categorias': _filter_categorias_example,
        'product_list': current_product_list, 'search_query': search_query,
        'selected_category_id': selected_category_id, 'selected_category_name': selected_category_name,
    }
    return render(request, 'comprador/pagina_busca_produto.html', context)

@login_required
def detalhes_produto(request, produto_id):
    produto_encontrado_original = None
    for p in _placeholder_all_products: 
        if p.get('id') == produto_id: produto_encontrado_original = p; break
    if not produto_encontrado_original: raise Http404("Produto não encontrado.")
    
    produto_encontrado_list = _enrich_product_data([produto_encontrado_original], request.session, _simulacao_ids_favoritados)
    produto_encontrado = produto_encontrado_list[0] if produto_encontrado_list else None
    if not produto_encontrado: raise Http404("Erro ao processar dados do produto.")
        
    context = {
        'produto': produto_encontrado,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'comprador/detalhes_produto.html', context)

@login_required
def adicionar_aos_desejos(request, produto_id):
    global _simulacao_ids_favoritados
    produto_id = int(produto_id)
    if produto_id not in _simulacao_ids_favoritados:
        _simulacao_ids_favoritados.append(produto_id)
        messages.success(request, "Produto adicionado à sua lista de desejos!")
    else: messages.info(request, "Este produto já está na sua lista de desejos.")
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:lista_desejos'))

@login_required
def remover_dos_desejos(request, produto_id):
    global _simulacao_ids_favoritados
    produto_id = int(produto_id)
    if produto_id in _simulacao_ids_favoritados:
        _simulacao_ids_favoritados.remove(produto_id)
        messages.success(request, "Produto removido da sua lista de desejos!")
    else: messages.info(request, "Este produto não estava na sua lista de desejos.")
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:lista_desejos'))

@login_required
def lista_desejos(request):
    if request.user.is_staff: logout(request); messages.error(request, "Página não disponível."); return redirect('marketplace:landing_page')
    nome_usuario = request.user.first_name or request.user.username
    produtos_favoritados_list_original = [p for p in _placeholder_all_products if p.get('id') in _simulacao_ids_favoritados]
    produtos_favoritados_list = _enrich_product_data(produtos_favoritados_list_original, request.session, _simulacao_ids_favoritados)
    context = {'nome_usuario': nome_usuario, 'produtos_favoritados': produtos_favoritados_list }
    return render(request, 'comprador/lista_desejos.html', context)

@login_required
def adicionar_ao_carrinho(request, produto_id):
    produto_selecionado = None
    for p in _placeholder_all_products:
        if p.get('id') == produto_id: produto_selecionado = p; break
    if not produto_selecionado:
        messages.error(request, "Produto não encontrado!"); return redirect(request.META.get('HTTP_REFERER', 'marketplace:pagina_inicial_comprador'))
    
    carrinho = request.session.get('carrinho', {})
    item_id_str = str(produto_id)
    quantidade_form = 1

    if request.method == 'POST':
        try:
            quantidade_form = int(request.POST.get('quantidade', 1))
            if quantidade_form < 1: quantidade_form = 1
        except ValueError: quantidade_form = 1
    
    if item_id_str in carrinho:
        if request.method == 'POST': carrinho[item_id_str]['quantidade'] = quantidade_form
        else: carrinho[item_id_str]['quantidade'] = carrinho[item_id_str].get('quantidade', 0) + 1 
        messages.success(request, f"'{produto_selecionado['nome']}' atualizado no carrinho.")
    else:
        carrinho[item_id_str] = {
            'id': produto_selecionado['id'], 'nome': produto_selecionado['nome'],
            'preco': float(produto_selecionado['preco']), 'quantidade': quantidade_form,
            'imagem': produto_selecionado.get('imagem_arquivo_local') or produto_selecionado.get('imagem_url'),
            'tipo_imagem': 'local' if produto_selecionado.get('imagem_arquivo_local') else 'url'
        }
        messages.success(request, f"'{produto_selecionado['nome']}' adicionado ao carrinho!")
    request.session['carrinho'] = carrinho
    _update_cart_item_count(request)
    request.session.modified = True 
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:pagina_inicial_comprador'))

@login_required
def remover_do_carrinho(request, item_id):
    carrinho = request.session.get('carrinho', {})
    item_id_str = str(item_id)
    if item_id_str in carrinho:
        nome_produto_removido = carrinho[item_id_str].get('nome', 'Produto')
        del carrinho[item_id_str]
        request.session['carrinho'] = carrinho
        _update_cart_item_count(request)
        request.session.modified = True
        messages.success(request, f"'{nome_produto_removido}' removido do carrinho.")
    else:
        messages.info(request, "Item não encontrado no carrinho.")
    return redirect('marketplace:ver_carrinho')

@login_required
def ver_carrinho(request):
    carrinho_session = request.session.get('carrinho', {}); 
    itens_carrinho = []; total_carrinho = 0;
    _update_cart_item_count(request) # Garante que num_itens_carrinho na sessão está atualizado

    for item_id_str, item_data in carrinho_session.items(): # Renomeado item_id para item_id_str
        try:
            preco = float(item_data.get('preco', 0))
            quantidade = int(item_data.get('quantidade', 0))
            if quantidade <= 0: 
                if item_id_str in request.session.get('carrinho', {}): # Use item_id_str
                     del request.session['carrinho'][item_id_str]
                     request.session.modified = True
                continue
            subtotal = preco * quantidade
            itens_carrinho.append({
                'id': item_data.get('id'), 'nome': item_data.get('nome'),
                'preco_unitario': preco, 'quantidade': quantidade,
                'subtotal': subtotal, 'imagem': item_data.get('imagem'), 
                'tipo_imagem': item_data.get('tipo_imagem')
            })
            total_carrinho += subtotal
        except (ValueError, TypeError):
            messages.error(request, f"Item inválido no carrinho: {item_data.get('nome', 'ID '+item_id_str)}")
            if item_id_str in request.session.get('carrinho', {}): # Use item_id_str
                del request.session['carrinho'][item_id_str]
                request.session.modified = True
            continue
    
    context = {
        'itens_carrinho': itens_carrinho, 
        'total_carrinho': total_carrinho,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'comprador/carrinho.html', context)

@login_required
def comprador_logout(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    if 'carrinho' in request.session: del request.session['carrinho']
    if 'num_itens_carrinho' in request.session: del request.session['num_itens_carrinho']
    request.session.modified = True
    return redirect('marketplace:landing_page')