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
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('marketplace:admin_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff: # Verifica se é staff
            login(request, user)
            return redirect(request.GET.get('next', 'marketplace:admin_dashboard')) # CORRETO: Redireciona após login
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
    recent_users = User.objects.order_by('-date_joined')[:3]
    recent_anuncios = Anuncio.objects.order_by('-data_criacao')[:3]
    total_compradores = Perfil.objects.filter(tipo='comprador').count()
    total_vendedores = Perfil.objects.filter(tipo='vendedor').count()
    total_anuncios_ativos = Anuncio.objects.filter(estoque__gt=0).count() # Exemplo: status='ativo'
    context = {
        'recent_users': recent_users,
        'recent_anuncios': recent_anuncios,
        'total_compradores': total_compradores,
        'total_vendedores': total_vendedores,
        'total_anuncios_ativos': total_anuncios_ativos,
    }
    return render(request, 'admin/dashboard.html', context)

# As views abaixo são para exibir páginas, então render() está CORRETO.

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_anuncios(request):
    # Adicione aqui o contexto necessário para o template, se houver
    # context = {'anuncios': Anuncio.objects.all()}
    # return render(request, "admin/anuncios.html", context)
    anuncios = Anuncio.objects.all().select_related('usuario', 'categoria').order_by('-data_criacao')
    context = {'anuncios_list': anuncios}
    return render(request, "admin/anuncios.html", context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_usuarios(request):
    usuarios = User.objects.all().select_related('perfil').order_by('-date_joined')
    context = {'usuarios_list': usuarios}
    return render(request, "admin/usuarios.html", context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_usuario(request, user_id=None):
    # Geralmente, uma view "gerenciar_X" pode receber um ID para gerenciar um item específico
    # ou pode ser uma página com um formulário para criar/editar.
    # Se receber um ID, você o pegaria aqui (ex: request.GET.get('id') ou da URL).
    if user_id:
        target_user = get_object_or_404(User.objects.select_related('perfil'), pk=user_id)
        context = {'target_user': target_user}
        return render(request, "admin/gerenciar_usuario.html", context)
    messages.info(request, "Para gerenciar um usuário, selecione um da lista.")
    return redirect('marketplace:admin_usuarios')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reportes(request):
    reportes = Reporte.objects.filter(status__in=['aberto', 'em_analise']).select_related('usuario', 'anuncio').order_by('-data_criacao')
    context = {'reportes_list': reportes}
    return render(request, "admin/reportes.html", context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_reporte(request, reporte_id=None):
    if reporte_id:
        reporte = get_object_or_404(Reporte.objects.select_related('usuario', 'anuncio__usuario', 'anuncio__categoria').prefetch_related('fotos'), pk=reporte_id)
        context = {'reporte': reporte}
        return render(request, "admin/gerenciar_reporte.html", context)
    messages.error(request, "ID do reporte não fornecido.")
    return redirect('marketplace:admin_reportes')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reportes_arquivados(request):
    reportes_arquivados = Reporte.objects.filter(status='arquivado').select_related('usuario', 'anuncio').order_by('-data_criacao')
    context = {'reportes_list': reportes_arquivados}
    return render(request, "admin/reportes_arquivados.html", context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_reporte_arquivado(request, reporte_id=None):
    if reporte_id:
        reporte = get_object_or_404(Reporte.objects.select_related('usuario', 'anuncio__usuario', 'anuncio__categoria').prefetch_related('fotos'), pk=reporte_id, status='arquivado')
        context = {'reporte': reporte}
        return render(request, "admin/gerenciar_reporte_arquivado.html", context) # Template específico
    messages.error(request, "ID do reporte arquivado não fornecido.")
    return redirect('marketplace:admin_reportes_arquivados')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_pedidos(request):
    pedidos = Pedido.objects.exclude(status_entrega='entregue').select_related('usuario').order_by('-data_criacao')
    context = {'pedidos_list': pedidos}
    return render(request, "admin/pedidos.html", context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_pedido(request, pedido_id=None):
    if pedido_id:
        pedido = get_object_or_404(Pedido.objects.select_related('usuario').prefetch_related('itens__anuncio'), pk=pedido_id)
        context = {'pedido': pedido}
        return render(request, "admin/gerenciar_pedido.html", context)
    messages.error(request, "ID do pedido não fornecido.")
    return redirect('marketplace:admin_pedidos')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_pedidos_finalizados(request):
    pedidos_finalizados = Pedido.objects.filter(status_entrega='entregue').select_related('usuario').order_by('-data_criacao')
    context = {'pedidos_list': pedidos_finalizados}
    return render(request, "admin/pedidos_finalizados.html", context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_pedido_finalizado(request, pedido_id=None):
    if pedido_id:
        pedido = get_object_or_404(Pedido.objects.select_related('usuario').prefetch_related('itens__anuncio'), pk=pedido_id, status_entrega='entregue')
        context = {'pedido': pedido}
        return render(request, "admin/gerenciar_pedido_finalizado.html", context) # Template específico
    messages.error(request, "ID do pedido finalizado não fornecido.")
    return redirect('marketplace:admin_pedidos_finalizados')

# View para processar o logout do administrador
@login_required # Garante que apenas usuários logados possam tentar deslogar
def admin_logout(request):
    logout(request)
    messages.info(request, "Você saiu da área administrativa.")
    return redirect('marketplace:admin_login') # CORRETO: Redireciona para a página de login após logout


# ========================
# VIEWS DO COMPRADOR
# ========================
def comprador_login(request):
    if is_comprador(request.user):
        return redirect('marketplace:pagina_inicial_comprador')
    
    if request.method == 'POST':
        email_username = request.POST.get('username') # Campo 'username' do form é usado como username para auth
        senha = request.POST.get('password')
        
        user = authenticate(request, username=email_username, password=senha) # Usa User do Django
        if user is not None:
            if hasattr(user, 'perfil') and user.perfil.tipo == 'comprador':
                login(request, user)
                return redirect(request.GET.get('next','marketplace:pagina_inicial_comprador')) # ADICIONADO: redirect para 'next'
            elif user.is_staff: 
                 messages.error(request, 'Conta de administrador. Use o login de admin.')
            else:
                messages.error(request, 'Este login não é para compradores ou o perfil está incompleto.')
        else:
            messages.error(request, 'Email ou senha inválidos.')
        return redirect('marketplace:comprador_login') 
    return render(request, 'comprador/login.html')

@transaction.atomic
def comprador_cadastro(request):
    if is_comprador(request.user): # ADICIONADO: usa helper
        return redirect('marketplace:pagina_inicial_comprador')

    if request.method == 'POST':
        # Coleta dos dados (mantida, mas com strip e tratamento de erro para idade)
        nome = request.POST.get('nome', '').strip()
        idade_str = request.POST.get('idade', '').strip()
        cpf = request.POST.get('cpf', '').strip()
        curso = request.POST.get('curso', '').strip()
        ra = request.POST.get('ra', '').strip()
        email = request.POST.get('email', '').strip().lower() # ADICIONADO: .lower()
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # ADICIONADO: Validação de idade
        idade = None
        if idade_str:
            try:
                idade = int(idade_str)
                if idade < 16:
                    messages.error(request, 'Você precisa ter pelo menos 16 anos para se cadastrar.')
                    return render(request, 'comprador/cadastro.html', request.POST) # Retorna com dados
            except ValueError:
                messages.error(request, 'Idade inválida. Por favor, insira um número.')
                return render(request, 'comprador/cadastro.html', request.POST) # Retorna com dados

        # Validações (mantidas e melhoradas)
        if not all([nome, idade_str, cpf, email, senha, confirmar_senha]): # Curso e RA podem ser opcionais
            messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
            return render(request, 'comprador/cadastro.html', request.POST)
        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'comprador/cadastro.html', request.POST)
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists(): # Verifica username e email
            messages.error(request, 'Já existe um usuário com este email.')
            return render(request, 'comprador/cadastro.html', request.POST)
        
        try:
            user = User.objects.create_user(username=email, email=email, password=senha)
            user.first_name = nome # O nome completo vai para first_name
            user.save()

            perfil, created_perfil = Perfil.objects.get_or_create(user=user)
            perfil.tipo = 'comprador'
            perfil.idade = idade
            perfil.cpf = cpf
            perfil.curso = curso
            perfil.ra = ra
            perfil.save()
            
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso! Você já está logado.')
            return redirect('marketplace:pagina_inicial_comprador')
        except Exception as e:
            # ADICIONADO: Log do erro (importante para debug)
            # logger.error(f"Erro no cadastro do comprador: {e}")
            messages.error(request, 'Ocorreu um erro inesperado durante o cadastro. Tente novamente.')
            return render(request, 'comprador/cadastro.html', request.POST) # Retorna com dados
            
    return render(request, 'comprador/cadastro.html')

#FUNÇÃO _enrich_products_with_favorite_status MOVIDA PARA DENTRO DAS VIEWS

@login_required
def home_comprador(request):
    if not is_comprador(request.user): 
        logout(request)
        messages.error(request, "Área restrita a compradores.")
        return redirect('marketplace:comprador_login') # Redireciona para login de comprador
        
    nome_usuario = request.user.first_name or request.user.username
    
    selected_category_slug = request.GET.get('categoria') 
    search_query = request.GET.get('q_search', '').strip()

    anuncios_list = Anuncio.objects.filter(estoque__gt=0).select_related('usuario__perfil', 'categoria').order_by('-data_criacao') # Adicione .filter(status='ativo') se tiver status

    if selected_category_slug and selected_category_slug != 'todos':
        anuncios_list = anuncios_list.filter(categoria__slug=selected_category_slug)
    
    if search_query: 
        anuncios_list = anuncios_list.filter(
            Q(titulo__icontains=search_query) |
            Q(descricao__icontains=search_query) |
            Q(categoria__nome_exibicao__icontains=search_query) |
            Q(usuario__first_name__icontains=search_query) | # Busca no nome do vendedor
            Q(usuario__username__icontains=search_query)    # Busca no email/username do vendedor
        ).distinct()
    
    favorited_anuncio_ids = []
    if request.user.is_authenticated:
        favorited_anuncio_ids = ItemListaDesejos.objects.filter(usuario=request.user).values_list('anuncio_id', flat=True)

    anuncios_display = []
    for anuncio_obj in anuncios_list:
        anuncios_display.append({
            'obj': anuncio_obj,
            'is_favorited': anuncio_obj.pk in favorited_anuncio_ids
        })

    categorias = Categoria.objects.all().order_by('nome_exibicao')

    context = {
        'nome_usuario': nome_usuario,
        'filter_categorias': categorias, # Passa objetos Categoria
        'anuncios_display': anuncios_display, # Passa lista de dicionários
        'selected_category_slug': selected_category_slug, # Passa o slug
        'search_query': search_query,
    }
    return render(request, 'comprador/home_comprador.html', context)

@login_required
def pagina_busca_produto(request):
    if not is_comprador(request.user):
        logout(request)
        messages.error(request, "Área restrita a compradores.")
        return redirect('marketplace:comprador_login')
        
    nome_usuario = request.user.first_name or request.user.username
    selected_category_slug = request.GET.get('categoria')
    search_query = request.GET.get('q_search', '').strip()
    
    anuncios_list = Anuncio.objects.filter(estoque__gt=0).select_related('usuario__perfil', 'categoria')

    selected_category_name = None # Para exibir o nome da categoria filtrada
    if selected_category_slug and selected_category_slug != 'todos':
        anuncios_list = anuncios_list.filter(categoria__slug=selected_category_slug)
        try:
            cat_obj = Categoria.objects.get(slug=selected_category_slug)
            selected_category_name = cat_obj.nome_exibicao
        except Categoria.DoesNotExist:
            pass # Slug inválido, a busca ainda pode ocorrer sem filtro de categoria
    
    if search_query:
        anuncios_list = anuncios_list.filter(
             Q(titulo__icontains=search_query) |
             Q(descricao__icontains=search_query) |
             Q(categoria__nome_exibicao__icontains=search_query) |
             Q(usuario__first_name__icontains=search_query) |
             Q(usuario__username__icontains=search_query)
        ).distinct()
    elif not selected_category_slug and not search_query: # Se acessou /busca/ sem parâmetros
        anuncios_list = Anuncio.objects.none() # Ou mostre todos, ou uma mensagem para buscar


    favorited_anuncio_ids = []
    if request.user.is_authenticated:
        favorited_anuncio_ids = ItemListaDesejos.objects.filter(usuario=request.user).values_list('anuncio_id', flat=True)
    
    anuncios_display = []
    for anuncio_obj in anuncios_list:
        anuncios_display.append({
            'obj': anuncio_obj,
            'is_favorited': anuncio_obj.pk in favorited_anuncio_ids
        })
        
    categorias = Categoria.objects.all().order_by('nome_exibicao')
    
    context = {
        'nome_usuario': nome_usuario,
        'filter_categorias': categorias,
        'anuncios_display': anuncios_display,
        'search_query': search_query,
        'selected_category_slug': selected_category_slug,
        'selected_category_name': selected_category_name, # Para o título da busca
    }
    return render(request, 'comprador/pagina_busca_produto.html', context)

@login_required
def detalhes_produto(request, produto_id):
    anuncio = get_object_or_404(Anuncio.objects.select_related('usuario__perfil', 'categoria'), pk=produto_id)
    
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = ItemListaDesejos.objects.filter(usuario=request.user, anuncio=anuncio).exists()
    
    avaliacoes = Avaliacao.objects.filter(anuncio=anuncio).select_related('usuario').order_by('-data_criacao')
    
    fotos_adicionais = anuncio.fotos_adicionais.all() # Usando related_name='fotos_adicionais' do modelo Foto

    if request.method == 'POST' and request.user.is_authenticated:
        # Identificar se é o formulário de avaliação, ex: por um name no botão de submit
        if 'submit_avaliacao' in request.POST:
            rating_str = request.POST.get('rating')
            comentario = request.POST.get('comment', '').strip()

            if rating_str and comentario:
                try:
                    rating = int(rating_str)
                    if 1 <= rating <= 5:
                        # Verifica se o usuário já avaliou
                        if not Avaliacao.objects.filter(anuncio=anuncio, usuario=request.user).exists():
                            Avaliacao.objects.create(
                                anuncio=anuncio,
                                usuario=request.user,
                                rating=rating,
                                comentario=comentario
                            )
                            messages.success(request, "Sua avaliação foi enviada!")
                            return redirect('marketplace:detalhes_produto', produto_id=anuncio.pk) # Redireciona para evitar re-POST
                        else:
                            messages.info(request, "Você já avaliou este produto.")
                    else:
                        messages.error(request, "A nota deve ser entre 1 e 5.")
                except ValueError:
                    messages.error(request, "Nota inválida.")
            else:
                messages.error(request, "Por favor, forneça uma nota e um comentário para a avaliação.")
        # Adicionar aqui lógica para "Adicionar ao Carrinho" se o form estiver nesta página
        # elif 'add_to_cart' in request.POST:
            # ...

    context = {
        'anuncio': anuncio, # Passa o objeto Anuncio
        'is_favorited': is_favorited,
        'avaliacoes': avaliacoes,
        'fotos_adicionais': fotos_adicionais,
        'nome_usuario': request.user.first_name or request.user.username if request.user.is_authenticated else None,
    }
    return render(request, 'comprador/detalhes_produto.html', context)

# --- VIEWS PARA LISTA DE DESEJOS (SIMULADAS) ---
@login_required
def adicionar_aos_desejos(request, produto_id): # produto_id refere-se a Anuncio.id
    if not is_comprador(request.user):
        messages.error(request, "Apenas compradores podem adicionar à lista de desejos.")
        return redirect(request.META.get('HTTP_REFERER', 'marketplace:pagina_inicial_comprador'))

    anuncio = get_object_or_404(Anuncio, pk=produto_id)
    # Cria o item na lista de desejos, não faz nada se já existir
    item, created = ItemListaDesejos.objects.get_or_create(usuario=request.user, anuncio=anuncio)
    
    if created:
        messages.success(request, f"'{anuncio.titulo}' foi adicionado à sua lista de desejos!")
    else:
        messages.info(request, f"'{anuncio.titulo}' já estava na sua lista de desejos.")
    
    # Redireciona para a página anterior ou para a lista de desejos
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:lista_desejos'))

@login_required
def remover_dos_desejos(request, produto_id):
    if not is_comprador(request.user):
        messages.error(request, "Apenas compradores podem remover da lista de desejos.")
        return redirect(request.META.get('HTTP_REFERER', 'marketplace:pagina_inicial_comprador'))

    anuncio = get_object_or_404(Anuncio, pk=produto_id)
    try:
        item = ItemListaDesejos.objects.get(usuario=request.user, anuncio=anuncio)
        item.delete()
        messages.success(request, f"'{anuncio.titulo}' foi removido da sua lista de desejos!")
    except ItemListaDesejos.DoesNotExist:
        messages.info(request, f"'{anuncio.titulo}' não estava na sua lista de desejos.")
        
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:lista_desejos'))

@login_required
def lista_desejos(request):
    if not is_comprador(request.user):
        logout(request)
        messages.error(request, "Página não disponível para este tipo de usuário.")
        return redirect('marketplace:comprador_login')
        
    nome_usuario = request.user.first_name or request.user.username
    
    # Busca os anúncios favoritados pelo usuário
    itens_desejados = ItemListaDesejos.objects.filter(usuario=request.user).select_related(
        'anuncio', 
        'anuncio__usuario__perfil', # Para nome do vendedor
        'anuncio__categoria'      # Para nome da categoria
    ).order_by('-data_adicao')
    
    anuncios_favoritados_display = []
    for item_desejado in itens_desejados:
        anuncios_favoritados_display.append({
            'obj': item_desejado.anuncio, # O objeto Anuncio
            'is_favorited': True # Por definição, todos aqui são favoritados
            # Adicione outros dados do anúncio que o template precise diretamente aqui se preferir
        })

    context = {
        'nome_usuario': nome_usuario,
        'anuncios_favoritados_display': anuncios_favoritados_display, # Lista de dicionários
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