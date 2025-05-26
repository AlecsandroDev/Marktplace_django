from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import Http404
import copy

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

_simulacao_ids_favoritados = [1, 4] 

_simulacao_perfil_extra_usuario_atual = {
    'idade': '21', 
    'cpf': '111.222.333-44',   
    'curso': 'Engenharia de Software', 
    'ra': '654321',    
    'foto_url': None 
}

_simulacao_avaliacoes_produtos = {
    1: [ 
        {'autor_username': 'ana_silva', 'autor_nome': 'Ana Paula', 'nota': 5, 'comentario': 'Maravilhoso! O melhor bolo de cenoura que já comi.', 'data': '22/05/2025'},
        {'autor_username': 'carlos_santos', 'autor_nome': 'Carlos Silva', 'nota': 4, 'comentario': 'Muito bom, mas a cobertura poderia ser mais generosa.', 'data': '21/05/2025'},
    ],
    2: [ 
        {'autor_username': 'user_teste', 'autor_nome': 'Fernanda Lima', 'nota': 5, 'comentario': 'Crocante e super recheada, perfeita!', 'data': '23/05/2025'},
    ]
}

_simulacao_meus_pedidos = [
    {
        'id': 2025001, 'data_pedido': '20 de Maio, 2025', 'total': 50.50, 'status': 'Concluído',
        'resumo_itens': 'Bolo de Cenoura Delicioso, Coxinha Crocante (4)',
        'itens': [
            {'produto_id': 1, 'nome': 'Bolo de Cenoura Delicioso', 'quantidade': 1, 'preco_unitario': 22.50, 'subtotal': 22.50},
            {'produto_id': 2, 'nome': 'Coxinha Crocante (Unidade)', 'quantidade': 4, 'preco_unitario': 7.00, 'subtotal': 28.00}
        ],
        'endereco_entrega': 'Rua da Universidade, 123, Bloco A, Apto 101, Cidade Universitária',
        'metodo_pagamento': 'Cartão de Crédito final **** 1234'
    },
    {
        'id': 2025002, 'data_pedido': '23 de Maio, 2025', 'total': 16.00, 'status': 'Pendente',
        'resumo_itens': 'Mini Pizza Calabresa (2)',
        'itens': [
            {'produto_id': 6, 'nome': 'Mini Pizza Calabresa', 'quantidade': 2, 'preco_unitario': 8.00, 'subtotal': 16.00}
        ],
        'endereco_entrega': 'Av. dos Estudantes, 789, Cantina Central, Cidade Universitária',
        'metodo_pagamento': 'PIX'
    },
    {
        'id': 2025003, 'data_pedido': '15 de Maio, 2025', 'total': 6.50, 'status': 'Cancelado',
        'resumo_itens': 'Empada de Palmito (1)',
        'itens': [
            {'produto_id': 7, 'nome': 'Empada de Palmito', 'quantidade': 1, 'preco_unitario': 6.50, 'subtotal': 6.50}
        ],
        'endereco_entrega': 'Rua da Biblioteca, S/N, Fundos, Cidade Universitária',
        'metodo_pagamento': 'Dinheiro'
    },
]

def _update_cart_item_count(request):
    carrinho = request.session.get('carrinho', {})
    request.session['num_itens_carrinho'] = len(carrinho)
    request.session.modified = True

def _enrich_product_data(product_list_original, request_session, user_favorites_ids):
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
    if request.user.is_authenticated and not request.user.is_staff: return redirect('marketplace:pagina_inicial_comprador')
    if request.method == 'POST':
        email = request.POST.get('username'); senha = request.POST.get('password')
        user = authenticate(request, username=email, password=senha)
        if user is not None:
            if not user.is_staff:
                login(request, user); _update_cart_item_count(request) 
                next_url = request.GET.get('next');
                if next_url: return redirect(next_url)
                return redirect('marketplace:pagina_inicial_comprador')
            else: messages.error(request, 'Conta de administrador.'); return redirect('marketplace:comprador_login')
        else: messages.error(request, 'Email ou senha inválidos.'); return redirect('marketplace:comprador_login')
    return render(request, 'comprador/login.html')

def comprador_cadastro(request):
    if request.user.is_authenticated and not request.user.is_staff: return redirect('marketplace:pagina_inicial_comprador')
    if request.method == 'POST':
        nome = request.POST.get('nome'); idade = request.POST.get('idade'); cpf = request.POST.get('cpf')
        curso = request.POST.get('curso'); ra = request.POST.get('ra'); email = request.POST.get('email')
        senha = request.POST.get('senha'); confirmar_senha = request.POST.get('confirmar_senha')
        if not all([nome, idade, cpf, curso, ra, email, senha, confirmar_senha]): messages.error(request, 'Todos os campos são obrigatórios.'); return redirect('marketplace:comprador_cadastro')
        if senha != confirmar_senha: messages.error(request, 'As senhas não coincidem.'); return redirect('marketplace:comprador_cadastro')
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists(): messages.error(request, 'Já existe um usuário com este email.'); return redirect('marketplace:comprador_cadastro')
        try:
            idade_int = int(idade)
            if idade_int < 16: messages.error(request, 'Você precisa ter pelo menos 16 anos.'); return redirect('marketplace:comprador_cadastro')
        except ValueError: messages.error(request, 'Idade inválida.'); return redirect('marketplace:comprador_cadastro')
        try:
            user = User.objects.create_user(username=email, email=email, password=senha)
            user.first_name = nome; user.save(); 
            global _simulacao_perfil_extra_usuario_atual
            _simulacao_perfil_extra_usuario_atual['idade'] = idade; _simulacao_perfil_extra_usuario_atual['cpf'] = cpf
            _simulacao_perfil_extra_usuario_atual['curso'] = curso; _simulacao_perfil_extra_usuario_atual['ra'] = ra
            login(request, user); _update_cart_item_count(request)
            messages.success(request, 'Cadastro realizado com sucesso! Você já está logado.')
            return redirect('marketplace:pagina_inicial_comprador')
        except Exception as e: messages.error(request, 'Ocorreu um erro inesperado.'); return redirect('marketplace:comprador_cadastro')
    return render(request, 'comprador/cadastro.html')

@login_required
def home_comprador(request):
    if request.user.is_staff: logout(request); messages.error(request, "Área restrita."); return redirect('marketplace:landing_page')
    nome_usuario = request.user.first_name or request.user.username; selected_category_id = request.GET.get('categoria')
    search_query = request.GET.get('q_search', '').strip(); product_list_to_display = list(_placeholder_all_products)
    if selected_category_id and selected_category_id != 'todos': product_list_to_display = [p for p in product_list_to_display if p.get('categoria_id') == selected_category_id]
    if search_query:
        search_results = []
        for p in product_list_to_display:
            if (search_query.lower() in p.get('nome', '').lower() or search_query.lower() in p.get('descricao_longa', '').lower() or search_query.lower() in p.get('vendedor_nome', '').lower()): search_results.append(p)
        product_list_to_display = search_results
    product_list_to_display = _enrich_product_data(product_list_to_display, request.session, _simulacao_ids_favoritados)
    context = {'nome_usuario': nome_usuario, 'filter_categorias': _filter_categorias_example, 'product_list': product_list_to_display, 'selected_category_id': selected_category_id, 'search_query': search_query }
    return render(request, 'comprador/home_comprador.html', context)

@login_required
def pagina_busca_produto(request):
    if request.user.is_staff: logout(request); messages.error(request, "Área restrita."); return redirect('marketplace:landing_page')
    nome_usuario = request.user.first_name or request.user.username; selected_category_id = request.GET.get('categoria')
    search_query = request.GET.get('q_search', '').strip(); current_product_list = []; selected_category_name = None
    if selected_category_id and selected_category_id != 'todos':
        for cat in _filter_categorias_example:
            if cat['id'] == selected_category_id: selected_category_name = cat['nome_exibicao']; break
    if search_query:
        current_product_list = list(_placeholder_all_products)
        if selected_category_id and selected_category_id != 'todos': current_product_list = [p for p in current_product_list if p.get('categoria_id') == selected_category_id]
        search_results = []
        for p in current_product_list:
            if (search_query.lower() in p.get('nome', '').lower() or search_query.lower() in p.get('descricao_longa', '').lower() or search_query.lower() in p.get('vendedor_nome', '').lower()): search_results.append(p)
        current_product_list = search_results
    elif selected_category_id and selected_category_id != 'todos': current_product_list = [p for p in _placeholder_all_products if p.get('categoria_id') == selected_category_id]
    current_product_list = _enrich_product_data(current_product_list, request.session, _simulacao_ids_favoritados)
    context = {'nome_usuario': nome_usuario, 'filter_categorias': _filter_categorias_example, 'product_list': current_product_list, 'search_query': search_query, 'selected_category_id': selected_category_id, 'selected_category_name': selected_category_name}
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
    # Adiciona avaliações simuladas ao contexto do produto para a página de detalhes do produto
    produto_encontrado['reviews'] = _simulacao_avaliacoes_produtos.get(produto_id, [])
    produto_encontrado['user_ja_avaliou'] = any(r['autor_username'] == request.user.username for r in produto_encontrado['reviews']) if request.user.is_authenticated else False
    context = {'produto': produto_encontrado, 'nome_usuario': request.user.first_name or request.user.username}
    return render(request, 'comprador/detalhes_produto.html', context)

@login_required
def adicionar_aos_desejos(request, produto_id):
    global _simulacao_ids_favoritados; produto_id = int(produto_id)
    if produto_id not in _simulacao_ids_favoritados: _simulacao_ids_favoritados.append(produto_id); messages.success(request, "Produto adicionado à lista de desejos!")
    else: messages.info(request, "Este produto já está na sua lista de desejos.")
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:lista_desejos'))

@login_required
def remover_dos_desejos(request, produto_id):
    global _simulacao_ids_favoritados; produto_id = int(produto_id)
    if produto_id in _simulacao_ids_favoritados: _simulacao_ids_favoritados.remove(produto_id); messages.success(request, "Produto removido da lista de desejos!")
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
    if not produto_selecionado: messages.error(request, "Produto não encontrado!"); return redirect(request.META.get('HTTP_REFERER', 'marketplace:pagina_inicial_comprador'))
    carrinho = request.session.get('carrinho', {}); item_id_str = str(produto_id); quantidade_form = 1
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
        carrinho[item_id_str] = {'id': produto_selecionado['id'], 'nome': produto_selecionado['nome'], 'preco': float(produto_selecionado['preco']), 'quantidade': quantidade_form, 'imagem': produto_selecionado.get('imagem_arquivo_local') or produto_selecionado.get('imagem_url'), 'tipo_imagem': 'local' if produto_selecionado.get('imagem_arquivo_local') else 'url'}
        messages.success(request, f"'{produto_selecionado['nome']}' adicionado ao carrinho!")
    request.session['carrinho'] = carrinho; _update_cart_item_count(request); request.session.modified = True 
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:pagina_inicial_comprador'))

@login_required
def remover_do_carrinho(request, item_id):
    carrinho = request.session.get('carrinho', {}); item_id_str = str(item_id)
    if item_id_str in carrinho:
        nome_produto_removido = carrinho[item_id_str].get('nome', 'Produto')
        del carrinho[item_id_str]; request.session['carrinho'] = carrinho
        _update_cart_item_count(request); request.session.modified = True
        messages.success(request, f"'{nome_produto_removido}' removido do carrinho.")
    else: messages.info(request, "Item não encontrado no carrinho.")
    return redirect('marketplace:ver_carrinho')

@login_required
def ver_carrinho(request):
    carrinho_session = request.session.get('carrinho', {}); itens_carrinho = []; total_carrinho = 0;
    _update_cart_item_count(request) 
    for item_id_str, item_data in carrinho_session.items():
        try:
            preco = float(item_data.get('preco', 0)); quantidade = int(item_data.get('quantidade', 0))
            if quantidade <= 0: 
                if item_id_str in request.session.get('carrinho', {}): del request.session['carrinho'][item_id_str]; request.session.modified = True
                continue
            subtotal = preco * quantidade
            itens_carrinho.append({'id': item_data.get('id'), 'nome': item_data.get('nome'), 'preco_unitario': preco, 'quantidade': quantidade, 'subtotal': subtotal, 'imagem': item_data.get('imagem'), 'tipo_imagem': item_data.get('tipo_imagem')})
            total_carrinho += subtotal
        except (ValueError, TypeError):
            messages.error(request, f"Item inválido no carrinho: ID {item_id_str}")
            if item_id_str in request.session.get('carrinho', {}): del request.session['carrinho'][item_id_str]; request.session.modified = True
            continue
    context = {'itens_carrinho': itens_carrinho, 'total_carrinho': total_carrinho, 'nome_usuario': request.user.first_name or request.user.username}
    return render(request, 'comprador/carrinho.html', context)

@login_required
def perfil_comprador(request):
    user = request.user
    perfil_extra_data = copy.deepcopy(_simulacao_perfil_extra_usuario_atual) 
    # if hasattr(user, 'userprofile') and user.userprofile.foto:
    #     perfil_extra_data['foto_url'] = user.userprofile.foto.url
    context = { 'user_obj': user, 'perfil_extra': perfil_extra_data, }
    return render(request, 'comprador/perfil.html', context)

@login_required
def editar_perfil(request):
    user = request.user
    global _simulacao_perfil_extra_usuario_atual
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        new_email = request.POST.get('email', user.email).strip()
        email_changed = False
        if new_email != user.email:
            if User.objects.filter(email=new_email).exclude(username=user.username).exists():
                messages.error(request, 'Este email já está em uso por outra conta.')
            else:
                user.email = new_email; user.username = new_email; email_changed = True
        user.save()
        if email_changed: messages.info(request, "Email (e login) atualizado com sucesso!")
        _simulacao_perfil_extra_usuario_atual['idade'] = request.POST.get('idade', _simulacao_perfil_extra_usuario_atual['idade'])
        _simulacao_perfil_extra_usuario_atual['cpf'] = request.POST.get('cpf', _simulacao_perfil_extra_usuario_atual['cpf'])
        _simulacao_perfil_extra_usuario_atual['curso'] = request.POST.get('curso', _simulacao_perfil_extra_usuario_atual['curso'])
        _simulacao_perfil_extra_usuario_atual['ra'] = request.POST.get('ra', _simulacao_perfil_extra_usuario_atual['ra'])
        if 'foto' in request.FILES: messages.info(request, "Nova foto de perfil recebida (simulação - não salva permanentemente).")
        messages.success(request, "Nome e email atualizados! Outras informações e foto são simuladas.")
        return redirect('marketplace:perfil_comprador')
    perfil_extra_data_form = copy.deepcopy(_simulacao_perfil_extra_usuario_atual)
    context = { 'user_obj': user, 'perfil_extra': perfil_extra_data_form }
    return render(request, 'comprador/editar_perfil.html', context)

@login_required
def encerrar_conta(request):
    if request.method == 'POST':
        logout(request) 
        messages.success(request, "Sua conta foi marcada para encerramento (Simulação). Você foi desconectado.")
        return redirect('marketplace:landing_page')
    return render(request, 'comprador/perfil_encerrar_conta_confirm.html')

@login_required
def meus_pedidos(request):
    if request.user.is_staff:
        logout(request); messages.error(request, "Página não disponível."); return redirect('marketplace:landing_page')
    pedidos_do_usuario = copy.deepcopy(_simulacao_meus_pedidos)
    for pedido in pedidos_do_usuario:
        for item_pedido in pedido.get('itens', []):
            produto_detalhe_original = next((p for p in _placeholder_all_products if p.get('id') == item_pedido.get('produto_id')), None)
            if produto_detalhe_original:
                item_pedido['imagem_arquivo_local'] = produto_detalhe_original.get('imagem_arquivo_local') # Adiciona para o resumo
    context = { 'pedidos': pedidos_do_usuario }
    return render(request, 'comprador/meus_pedidos.html', context)

@login_required
def detalhe_pedido(request, pedido_id):
    if request.user.is_staff:
        logout(request); messages.error(request, "Página não disponível."); return redirect('marketplace:landing_page')
    pedido_encontrado = None
    for pedido_simulado in _simulacao_meus_pedidos:
        if pedido_simulado.get('id') == pedido_id:
            pedido_encontrado = copy.deepcopy(pedido_simulado)
            for item_pedido in pedido_encontrado.get('itens', []):
                produto_detalhe = next((p for p in _placeholder_all_products if p.get('id') == item_pedido.get('produto_id')), None)
                if produto_detalhe:
                    item_pedido['imagem_arquivo_local'] = produto_detalhe.get('imagem_arquivo_local')
                    item_pedido['imagem_url'] = produto_detalhe.get('imagem_url')
                    item_pedido['descricao_longa_produto'] = produto_detalhe.get('descricao_longa', 'Descrição não disponível.')
                item_status = _enrich_product_data([{'id': item_pedido.get('produto_id')}], request.session, _simulacao_ids_favoritados)
                if item_status and len(item_status) > 0:
                    item_pedido['is_favorited'] = item_status[0].get('is_favorited', False)
                    item_pedido['is_in_cart'] = item_status[0].get('is_in_cart', False)
                item_pedido['avaliacoes_do_produto'] = _simulacao_avaliacoes_produtos.get(item_pedido.get('produto_id'), [])
                item_pedido['ja_avaliado_pelo_usuario_atual'] = any(
                    avaliacao.get('autor_username') == request.user.username 
                    for avaliacao in item_pedido['avaliacoes_do_produto']
                ) if request.user.is_authenticated else False
            break
    if not pedido_encontrado: raise Http404("Pedido não encontrado.")
    context = { 'pedido': pedido_encontrado }
    return render(request, 'comprador/detalhe_pedido.html', context)

@login_required
def pedir_novamente(request, pedido_id):
    if request.user.is_staff: messages.error(request, "Funcionalidade não disponível."); return redirect('marketplace:landing_page')
    pedido_antigo = next((p for p in _simulacao_meus_pedidos if p.get('id') == pedido_id), None)
    if not pedido_antigo: messages.error(request, "Pedido original não encontrado."); return redirect('marketplace:meus_pedidos')
    carrinho = request.session.get('carrinho', {}); itens_adicionados_count = 0; itens_nao_encontrados_nomes = []
    for item_do_pedido_antigo in pedido_antigo.get('itens', []):
        produto_id_original = item_do_pedido_antigo.get('produto_id'); quantidade_original = item_do_pedido_antigo.get('quantidade', 1)
        produto_atual_encontrado = next((p_atual for p_atual in _placeholder_all_products if p_atual.get('id') == produto_id_original), None)
        if produto_atual_encontrado:
            item_id_str = str(produto_id_original)
            carrinho[item_id_str] = {'id': produto_atual_encontrado['id'], 'nome': produto_atual_encontrado['nome'], 'preco': float(produto_atual_encontrado['preco']), 'quantidade': quantidade_original, 'imagem': produto_atual_encontrado.get('imagem_arquivo_local') or produto_atual_encontrado.get('imagem_url'), 'tipo_imagem': 'local' if produto_atual_encontrado.get('imagem_arquivo_local') else 'url'}
            itens_adicionados_count += 1
        else: itens_nao_encontrados_nomes.append(item_do_pedido_antigo.get('nome', f'ID {produto_id_original}'))
    if itens_adicionados_count > 0:
        request.session['carrinho'] = carrinho; _update_cart_item_count(request); request.session.modified = True
        messages.success(request, f"Itens do pedido anterior foram adicionados ao seu carrinho!")
    if itens_nao_encontrados_nomes: messages.warning(request, f"Alguns itens do pedido original não estão mais disponíveis: {', '.join(itens_nao_encontrados_nomes)}.")
    if not itens_adicionados_count and not itens_nao_encontrados_nomes: messages.info(request, "Não foi possível adicionar itens do pedido anterior ao carrinho.")
    return redirect('marketplace:ver_carrinho')

@login_required
def submeter_avaliacao_pedido(request, pedido_id, produto_id):
    if request.method == 'POST':
        nota = request.POST.get('rating')
        comentario = request.POST.get('comment')
        print(f"Avaliação SIMULADA para Pedido ID {pedido_id}, Produto ID {produto_id}: Nota={nota}, Comentário='{comentario}'")
        # Aqui você adicionaria à lista _simulacao_avaliacoes_produtos e talvez marcaria o item como avaliado
        # para este pedido específico (exigiria mais lógica na simulação).
        messages.success(request, "Sua avaliação foi enviada com sucesso! (Simulação)")
        return redirect('marketplace:detalhe_pedido', pedido_id=pedido_id)
    messages.error(request, "Não foi possível submeter a avaliação.")
    return redirect('marketplace:detalhe_pedido', pedido_id=pedido_id)

@login_required
def comprador_logout(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    if 'carrinho' in request.session: del request.session['carrinho']
    if 'num_itens_carrinho' in request.session: del request.session['num_itens_carrinho']
    request.session.modified = True
    return redirect('marketplace:landing_page')