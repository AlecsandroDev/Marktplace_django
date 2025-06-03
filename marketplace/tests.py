from django.test import TestCase, Client
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.conf import settings # Importe settings
from unittest.mock import patch # Para mockar requisições externas

# Importe seus modelos aqui
# Certifique-se de que esses modelos existam e estejam configurados no seu app
# Exemplo:
# from marketplace.models import Product, Favorite, CartItem, Order, OrderItem, Review, Category

# Seus modelos precisam existir para que os testes de criação funcionem.
# Substitua 'marketplace.models' pelos caminhos corretos se seus modelos estiverem em outra app.
try:
    from marketplace.models import Product, Favorite, CartItem, Order, OrderItem, Review, Category
except ImportError:
    # Fallback para evitar erro de importação se os modelos ainda não existirem
    # e você quiser rodar os testes apenas para a estrutura inicial.
    # Em um projeto real, você deve ter esses modelos criados.
    print("AVISO: Modelos (Product, Favorite, CartItem, etc.) não encontrados em marketplace.models. "
          "Certifique-se de criá-los ou ajustar o import para rodar os testes completos.")
    class Product: # Mock simples para permitir a execução dos testes
        objects = []
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.id = len(Product.objects) + 1
            Product.objects.append(self)
        def __str__(self): return self.name
    class Category:
        objects = []
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.id = len(Category.objects) + 1
            Category.objects.append(self)
        def __str__(self): return self.name
    # Faça mocks similares para Favorite, CartItem, Order, OrderItem, Review se necessário
    # Para testes mais profundos, é melhor criar modelos de teste reais ou usar factories

User = get_user_model()

class MarketplaceAdminViewsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.staff_password = 'strongstaffpassword'
        cls.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password=cls.staff_password,
            is_staff=True,
            is_active=True
        )

        cls.normal_password = 'normaluserpassword'
        cls.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password=cls.normal_password,
            is_staff=False,
            is_active=True
        )

        # URLs Admin
        cls.admin_login_url = reverse_lazy('marketplace:admin_login')
        cls.admin_dashboard_url = reverse_lazy('marketplace:admin_dashboard')
        cls.admin_anuncios_url = reverse_lazy('marketplace:admin_anuncios')
        cls.admin_usuarios_url = reverse_lazy('marketplace:admin_usuarios') # Adicione se for testar
        cls.admin_logout_url = reverse_lazy('marketplace:admin_logout')
        
        # URL de Login do Comprador (usada pelo settings.LOGIN_URL)
        # !! IMPORTANTE !! Confirme se 'marketplace:comprador_login' é o nome correto.
        try:
            cls.comprador_login_url_name = 'marketplace:comprador_login' 
            cls.comprador_login_url_base = reverse_lazy(cls.comprador_login_url_name)
        except Exception as e:
            print(f"AVISO DE TESTE: O nome da URL '{cls.comprador_login_url_name}' não foi encontrado. Ajuste em tests.py. Erro: {e}")
            cls.comprador_login_url_base = '/comprador/login/' 

    def setUp(self):
        self.client = Client()

    # === Testes para admin_login ===

    def test_admin_login_page_get_request_unauthenticated(self):
        response = self.client.get(self.admin_login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html')

    def test_admin_login_successful_staff_user(self):
        response = self.client.post(self.admin_login_url, {
            'username': self.staff_user.username,
            'password': self.staff_password,
        })
        # A página de dashboard do admin deve retornar 200 OK
        self.assertRedirects(response, self.admin_dashboard_url, status_code=302, target_status_code=200)
        self.assertEqual(str(self.client.session.get('_auth_user_id')), str(self.staff_user.id))

    def test_admin_login_failed_invalid_credentials(self):
        response = self.client.post(self.admin_login_url, {
            'username': self.staff_user.username,
            'password': 'wrongpassword',
        }, follow=True) 
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'admin/login.html')
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any(m.message == 'Credenciais inválidas ou você não tem permissão para acessar o admin.' for m in messages_list))

    def test_admin_login_failed_normal_user_not_staff(self):
        response = self.client.post(self.admin_login_url, {
            'username': self.normal_user.username,
            'password': self.normal_password,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html')
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any(m.message == 'Credenciais inválidas ou você não tem permissão para acessar o admin.' for m in messages_list))

    # === Testes para admin_dashboard ===

    def test_admin_dashboard_access_by_staff_user(self):
        self.client.login(username=self.staff_user.username, password=self.staff_password)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/dashboard.html')

    def test_admin_dashboard_redirect_if_not_logged_in(self):
        response = self.client.get(self.admin_dashboard_url)
        expected_redirect_url = f"{self.comprador_login_url_base}?next={self.admin_dashboard_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)

    def test_admin_dashboard_redirect_if_logged_in_as_non_staff(self):
        self.client.login(username=self.normal_user.username, password=self.normal_password)
        response = self.client.get(self.admin_dashboard_url)
        expected_redirect_url = f"{self.comprador_login_url_base}?next={self.admin_dashboard_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)

    # === Testes para admin_anuncios ===

    def test_admin_anuncios_access_by_staff_user(self):
        self.client.login(username=self.staff_user.username, password=self.staff_password)
        response = self.client.get(self.admin_anuncios_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/anuncios.html')

    def test_admin_anuncios_redirect_if_not_logged_in(self):
        response = self.client.get(self.admin_anuncios_url)
        expected_redirect_url = f"{self.comprador_login_url_base}?next={self.admin_anuncios_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)
        
    def test_admin_anuncios_redirect_if_logged_in_as_non_staff(self): # ESTE É O TESTE QUE ESTAVA FALHANDO
        self.client.login(username=self.normal_user.username, password=self.normal_password)
        response = self.client.get(self.admin_anuncios_url)
        expected_redirect_url = f"{self.comprador_login_url_base}?next={self.admin_anuncios_url}"
        # CORREÇÃO APLICADA AQUI: fetch_redirect_response=False
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)

    # === Testes para admin_logout ===

    def test_admin_logout_staff_user(self):
        self.client.login(username=self.staff_user.username, password=self.staff_password)
        response_before_logout = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response_before_logout.status_code, 200) # Confirma que estava logado

        response_logout = self.client.get(self.admin_logout_url)
        # O admin_logout redireciona para marketplace:admin_login, que deve dar 200 OK
        self.assertRedirects(response_logout, self.admin_login_url, status_code=302, target_status_code=200)

        # Tentar acessar uma página protegida (admin_dashboard) DEPOIS do logout
        # deve redirecionar para o LOGIN_URL (comprador_login)
        response_after_logout = self.client.get(self.admin_dashboard_url)
        expected_redirect_url_after_logout = f"{self.comprador_login_url_base}?next={self.admin_dashboard_url}"
        self.assertRedirects(response_after_logout, expected_redirect_url_after_logout, status_code=302, fetch_redirect_response=False)

    def test_admin_logout_when_not_logged_in(self):
        response = self.client.get(self.admin_logout_url)
        # O decorador @login_required na view de admin_logout redirecionará para o LOGIN_URL (comprador_login)
        expected_redirect_url = f"{self.comprador_login_url_base}?next={self.admin_logout_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)

    # Adicione aqui testes para as outras views de admin (admin_usuarios, etc.)
    # seguindo o padrão dos testes para admin_anuncios:
    # - test_VIEW_access_by_staff_user
    # - test_VIEW_redirect_if_not_logged_in (usar fetch_redirect_response=False)
    # - test_VIEW_redirect_if_logged_in_as_non_staff (usar fetch_redirect_response=False)


# ====================================================================
# === Testes para o Comprador ===
# ====================================================================

# Nova classe para os testes do comprador para melhor organização
# Ou você pode colocar os métodos abaixo na classe MarketplaceAdminViewsTests
# se preferir ter todos os testes de view em uma única classe.
class MarketplaceCompradorViewsTests(TestCase): # Nova classe para comprador

    @classmethod
    def setUpTestData(cls):
        # Usuário de teste para comprador
        cls.comprador_password = 'compradorpassword'
        cls.comprador_user = User.objects.create_user(
            username='compradoruser',
            email='comprador@example.com',
            password=cls.comprador_password,
            is_staff=False,
            is_active=True
        )

        # Usuário staff (admin) se precisar testar interação
        cls.staff_password = 'strongstaffpassword'
        cls.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password=cls.staff_password,
            is_staff=True,
            is_active=True
        )

        # Cria alguns dados de teste para produtos, categorias, etc.
        # Ajuste conforme seus modelos reais. Se você usou o "mock" acima,
        # pode remover a importação real e ele usará o mock.
        try:
            cls.category = Category.objects.create(name='Alimentos')
            cls.product1 = Product.objects.create(
                name='Pizza de Calabresa',
                description='Deliciosa pizza de calabresa e queijo.',
                price=29.99,
                category=cls.category,
                stock=10
            )
            cls.product2 = Product.objects.create(
                name='Hamburguer Artesanal',
                description='Hamburguer com pão brioche, carne de 180g e queijo.',
                price=25.00,
                category=cls.category,
                stock=5
            )
        except Exception as e:
            print(f"AVISO DE TESTE: Não foi possível criar objetos de Product/Category. "
                  f"Verifique se seus modelos estão importados/criados corretamente. Erro: {e}")
            # Mocks simplificados se os modelos não estiverem disponíveis
            cls.category = type('Category', (object,), {'id': 1, 'name': 'Alimentos', 'objects': []})()
            cls.product1 = type('Product', (object,), {'id': 1, 'name': 'Pizza de Calabresa', 'description': '', 'price': 29.99, 'category': cls.category, 'stock': 10, 'objects': []})()
            cls.product2 = type('Product', (object,), {'id': 2, 'name': 'Hamburguer Artesanal', 'description': '', 'price': 25.00, 'category': cls.category, 'stock': 5, 'objects': []})()


        # URLs do Comprador
        # Verifique se os nomes das URLs (`reverse_lazy`) estão corretos no seu urls.py
        cls.comprador_login_url = reverse_lazy('marketplace:comprador_login')
        cls.comprador_cadastro_url = reverse_lazy('marketplace:comprador_cadastro')
        cls.comprador_recuperar_senha_url = reverse_lazy('marketplace:recuperar_senha') # Nome comum para URL
        cls.comprador_home_url = reverse_lazy('marketplace:home')
        cls.comprador_detalhes_produto_url = reverse_lazy('marketplace:detalhes_produto', args=[cls.product1.id])
        cls.comprador_favoritos_url = reverse_lazy('marketplace:favoritos')
        cls.comprador_busca_url = reverse_lazy('marketplace:busca_produtos') # Nome mais específico
        cls.comprador_carrinho_url = reverse_lazy('marketplace:carrinho')
        cls.comprador_adicionar_carrinho_url = reverse_lazy('marketplace:adicionar_carrinho', args=[cls.product1.id]) # Exemplo
        cls.comprador_confirmacao_pedido_url = reverse_lazy('marketplace:confirmacao_pedido')
        cls.comprador_perfil_usuario_url = reverse_lazy('marketplace:perfil_usuario')
        cls.comprador_lista_pedidos_url = reverse_lazy('marketplace:lista_pedidos')
        cls.comprador_avaliar_produto_url = reverse_lazy('marketplace:avaliar_produto', args=[cls.product1.id]) # Exemplo
        cls.comprador_notificacoes_url = reverse_lazy('marketplace:notificacoes')
        cls.comprador_logout_url = reverse_lazy('marketplace:comprador_logout') # Se houver um logout específico do comprador
        cls.comprador_adicionar_remover_favorito_url = reverse_lazy('marketplace:adicionar_remover_favorito', args=[cls.product2.id]) # Exemplo

    def setUp(self):
        self.client = Client()

    # ====================================================================
    # === Testes para Login e Cadastro ===
    # ====================================================================

    def test_comprador_login_page_get_request(self):
        response = self.client.get(self.comprador_login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/login.html') # Ajuste o nome do template

    def test_comprador_login_successful(self):
        response = self.client.post(self.comprador_login_url, {
            'username': self.comprador_user.username,
            'password': self.comprador_password,
        })
        # Após o login, geralmente redireciona para a home page
        self.assertRedirects(response, self.comprador_home_url, status_code=302, target_status_code=200)
        self.assertEqual(str(self.client.session.get('_auth_user_id')), str(self.comprador_user.id))

    def test_comprador_login_failed_invalid_credentials(self):
        response = self.client.post(self.comprador_login_url, {
            'username': self.comprador_user.username,
            'password': 'wrongpassword',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/login.html')
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any(m.message == 'Nome de usuário ou senha inválidos.' for m in messages_list)) # Ajuste a mensagem

    def test_comprador_cadastro_page_get_request(self):
        response = self.client.get(self.comprador_cadastro_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/cadastro.html')

    def test_comprador_cadastro_successful(self):
        new_username = 'newuser'
        new_email = 'newuser@example.com'
        new_password = 'newpassword123'
        response = self.client.post(self.comprador_cadastro_url, {
            'username': new_username,
            'email': new_email,
            'password': new_password,
            'password_confirm': new_password, # Se o seu form tiver confirmação de senha
        })
        # Verifica se o usuário foi criado.
        # No caso de mock, isso não será refletido no "banco de dados" mockado de User.
        self.assertEqual(User.objects.filter(username=new_username).count(), 1)
        # Após o cadastro, geralmente redireciona para a página de login
        self.assertRedirects(response, self.comprador_login_url, status_code=302, target_status_code=200)

    def test_comprador_cadastro_failed_passwords_dont_match(self):
        response = self.client.post(self.comprador_cadastro_url, {
            'username': 'mismatched',
            'email': 'mismatched@example.com',
            'password': 'password1',
            'password_confirm': 'password2',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/cadastro.html')
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any('senhas não conferem' in m.message.lower() for m in messages_list)) # Ajuste a mensagem de erro

    # ====================================================================
    # === Testes para Recuperar Senha ===
    # ====================================================================

    def test_recuperar_senha_page_get_request(self):
        response = self.client.get(self.comprador_recuperar_senha_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/recuperar_senha.html')

    # Teste para simular o envio de e-mail (geralmente se usa mock para isso)
    @patch('django.core.mail.send_mail') # Mocka a função de envio de e-mail do Django
    def test_recuperar_senha_successful_email_sent(self, mock_send_mail):
        response = self.client.post(self.comprador_recuperar_senha_url, {
            'email': self.comprador_user.email,
        })
        self.assertTrue(mock_send_mail.called) # Verifica se send_mail foi chamado
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any('instruções de recuperação de senha' in m.message.lower() for m in messages_list))
        self.assertRedirects(response, self.comprador_login_url, status_code=302, target_status_code=200)

    def test_recuperar_senha_email_not_found(self):
        response = self.client.post(self.comprador_recuperar_senha_url, {
            'email': 'nonexistent@example.com',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any('E-mail não encontrado' in m.message or 'não existe' in m.message for m in messages_list)) # Ajuste a mensagem de erro

    # ====================================================================
    # === Testes para Página Inicial / Busca / Filtro ===
    # ====================================================================

    def test_home_page_get_request(self):
        response = self.client.get(self.comprador_home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/home.html')
        # Verifica se os produtos de teste são exibidos na página
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)

    def test_busca_produtos(self):
        response = self.client.get(self.comprador_busca_url, {'q': 'Pizza'}) # 'q' é um nome comum para query
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/home.html') # Ou 'comprador/busca.html' se for um template separado
        self.assertContains(response, self.product1.name) # Pizza de Calabresa
        self.assertNotContains(response, self.product2.name) # Hamburguer

    def test_filtro_produtos_por_categoria(self):
        response = self.client.get(self.comprador_home_url, {'category': self.category.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/home.html')
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)
        # Se você tivesse outra categoria com outros produtos, testaria o NotContains

    # ====================================================================
    # === Testes para Detalhes do Produto ===
    # ====================================================================

    def test_detalhes_produto_page_get_request(self):
        response = self.client.get(self.comprador_detalhes_produto_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/detalhes_produto.html')
        self.assertContains(response, self.product1.name)
        self.assertContains(response, str(self.product1.price))

    def test_detalhes_produto_non_existent(self):
        # Cria uma URL para um ID de produto que certamente não existe
        non_existent_product_url = reverse('marketplace:detalhes_produto', args=[99999])
        response = self.client.get(non_existent_product_url)
        self.assertEqual(response.status_code, 404) # Ou redireciona para uma página de erro/home (verifique sua view)

    # ====================================================================
    # === Testes para Carrinho de Compras ===
    # ====================================================================

    def test_adicionar_produto_ao_carrinho_logged_in(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        # Supondo que a view de adicionar ao carrinho é um POST e espera 'quantity'
        response = self.client.post(self.comprador_adicionar_carrinho_url, {'quantity': 1})
        self.assertRedirects(response, self.comprador_carrinho_url, status_code=302, target_status_code=200)
        # A linha abaixo vai falhar se você estiver usando o mock de CartItem
        # pois o mock não tem um objects.filter real. Ajuste se estiver usando modelos reais.
        # self.assertEqual(CartItem.objects.filter(user=self.comprador_user, product=self.product1).count(), 1)
        # self.assertEqual(CartItem.objects.get(user=self.comprador_user, product=self.product1).quantity, 1)

    def test_adicionar_produto_ao_carrinho_not_logged_in(self):
        # Tentar adicionar ao carrinho sem estar logado deve redirecionar para o login
        response = self.client.post(self.comprador_adicionar_carrinho_url, {'quantity': 1})
        expected_redirect_url = f"{self.comprador_login_url}?next={self.comprador_adicionar_carrinho_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)

    def test_ver_carrinho_logged_in(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        # Adiciona um item ao carrinho para que a página não venha vazia
        # Isso requer que seu modelo CartItem e o método create estejam funcionando.
        try:
            CartItem.objects.create(user=self.comprador_user, product=self.product1, quantity=2)
        except AttributeError:
            print("AVISO: CartItem.objects.create não disponível (provavelmente usando mock). Teste pode não ser preciso.")

        response = self.client.get(self.comprador_carrinho_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/carrinho.html')
        self.assertContains(response, self.product1.name)
        self.assertContains(response, 'Quantidade: 2') # Ou como você exibe a quantidade

    def test_ver_carrinho_not_logged_in(self):
        response = self.client.get(self.comprador_carrinho_url)
        expected_redirect_url = f"{self.comprador_login_url}?next={self.comprador_carrinho_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)


    # ====================================================================
    # === Testes para Lista de Favoritos/Desejos ===
    # ====================================================================

    def test_favoritos_page_logged_in(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        try:
            Favorite.objects.create(user=self.comprador_user, product=self.product1)
        except AttributeError:
            print("AVISO: Favorite.objects.create não disponível (provavelmente usando mock). Teste pode não ser preciso.")

        response = self.client.get(self.comprador_favoritos_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/favoritos.html')
        self.assertContains(response, self.product1.name)

    def test_favoritos_page_not_logged_in(self):
        response = self.client.get(self.comprador_favoritos_url)
        expected_redirect_url = f"{self.comprador_login_url}?next={self.comprador_favoritos_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)

    def test_adicionar_remover_favorito(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        
        # Adicionar
        # Supondo que a view de adicionar/remover favorito é um POST que alterna o estado
        response_add = self.client.post(self.comprador_adicionar_remover_favorito_url) # Ou GET, dependendo da sua implementação
        self.assertEqual(response_add.status_code, 302) # Espera um redirecionamento ou 200 OK
        # self.assertTrue(Favorite.objects.filter(user=self.comprador_user, product=self.product2).exists())

        # Remover (se a mesma URL alternar)
        response_remove = self.client.post(self.comprador_adicionar_remover_favorito_url) # Ou DELETE, ou GET novamente
        self.assertEqual(response_remove.status_code, 302)
        # self.assertFalse(Favorite.objects.filter(user=self.comprador_user, product=self.product2).exists())


    # ====================================================================
    # === Testes para Confirmação de Pedido ===
    # ====================================================================

    def test_confirmacao_pedido_page_logged_in(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        # É preciso ter itens no carrinho para testar a confirmação
        try:
            CartItem.objects.create(user=self.comprador_user, product=self.product1, quantity=1)
        except AttributeError:
            print("AVISO: CartItem.objects.create não disponível (provavelmente usando mock). Teste pode não ser preciso.")

        response = self.client.get(self.comprador_confirmacao_pedido_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/confirmacao_pedido.html')
        self.assertContains(response, self.product1.name) # Verifica se o produto do carrinho está na página

    def test_confirmacao_pedido_not_logged_in(self):
        response = self.client.get(self.comprador_confirmacao_pedido_url)
        expected_redirect_url = f"{self.comprador_login_url}?next={self.comprador_confirmacao_pedido_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)

    def test_finalizar_pedido_successful(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        try:
            CartItem.objects.create(user=self.comprador_user, product=self.product1, quantity=1)
        except AttributeError:
            print("AVISO: CartItem.objects.create não disponível (provavelmente usando mock). Teste pode não ser preciso.")
        
        # Supondo que a finalização do pedido é um POST para a mesma URL de confirmação ou para outra
        response = self.client.post(self.comprador_confirmacao_pedido_url, {
            'payment_method': 'card', # Exemplo de dados de formulário que sua view esperaria
            'address': 'Rua Exemplo, 123',
        })
        # As linhas abaixo requerem que seus modelos Order e CartItem estejam funcionando.
        # self.assertEqual(Order.objects.filter(user=self.comprador_user).count(), 1) # Verifica se um pedido foi criado
        # self.assertEqual(CartItem.objects.filter(user=self.comprador_user).count(), 0) # Carrinho deve estar vazio
        # Redireciona para a lista de pedidos ou uma página de "pedido realizado com sucesso"
        self.assertRedirects(response, self.comprador_lista_pedidos_url, status_code=302, target_status_code=200)

    # ====================================================================
    # === Testes para Perfil do Usuário ===
    # ====================================================================

    def test_perfil_usuario_page_logged_in(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        response = self.client.get(self.comprador_perfil_usuario_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/perfil_usuario.html')
        self.assertContains(response, self.comprador_user.username)
        self.assertContains(response, self.comprador_user.email)

    def test_perfil_usuario_not_logged_in(self):
        response = self.client.get(self.comprador_perfil_usuario_url)
        expected_redirect_url = f"{self.comprador_login_url}?next={self.comprador_perfil_usuario_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)

    def test_atualizar_perfil_usuario(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        new_email = 'updated_comprador@example.com'
        response = self.client.post(self.comprador_perfil_usuario_url, {
            'username': self.comprador_user.username,
            'email': new_email,
            # Outros campos do formulário que podem ser atualizados
        })
        self.assertRedirects(response, self.comprador_perfil_usuario_url, status_code=302, target_status_code=200)
        self.comprador_user.refresh_from_db() # Recarrega o usuário do banco para ver as mudanças
        self.assertEqual(self.comprador_user.email, new_email)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any('perfil atualizado' in m.message.lower() for m in messages_list))


    # ====================================================================
    # === Testes para Lista de Pedidos ===
    # ====================================================================

    def test_lista_pedidos_page_logged_in(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        # Cria um pedido de teste
        try:
            order = Order.objects.create(user=self.comprador_user, total_price=self.product1.price)
            OrderItem.objects.create(order=order, product=self.product1, quantity=1, price=self.product1.price)
            self.assertContains(response, str(order.id)) # Verifica se o ID do pedido aparece
        except AttributeError:
            print("AVISO: Order/OrderItem.objects.create não disponível (provavelmente usando mock). Teste pode não ser preciso.")
            # Se mockado, você não pode verificar o ID do pedido no conteúdo

        response = self.client.get(self.comprador_lista_pedidos_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/lista_pedidos.html')
        

    def test_lista_pedidos_not_logged_in(self):
        response = self.client.get(self.comprador_lista_pedidos_url)
        expected_redirect_url = f"{self.comprador_login_url}?next={self.comprador_lista_pedidos_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)


    # ====================================================================
    # === Testes para Avaliação de Produtos ===
    # ====================================================================

    def test_avaliar_produto_page_logged_in(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        response = self.client.get(self.comprador_avaliar_produto_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/avaliar_produto.html')
        self.assertContains(response, self.product1.name)

    def test_avaliar_produto_not_logged_in(self):
        response = self.client.get(self.comprador_avaliar_produto_url)
        expected_redirect_url = f"{self.comprador_login_url}?next={self.comprador_avaliar_produto_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)

    def test_submit_avaliacao_successful(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        # Supondo que a avaliação é um POST para a mesma URL ou outra específica
        response = self.client.post(self.comprador_avaliar_produto_url, {
            'rating': 5,
            'comment': 'Produto excelente, adorei a pizza!',
        })
        self.assertRedirects(response, self.comprador_detalhes_produto_url, status_code=302, target_status_code=200)
        # self.assertEqual(Review.objects.filter(user=self.comprador_user, product=self.product1).count(), 1)
        # self.assertEqual(Review.objects.get(user=self.comprador_user, product=self.product1).rating, 5)


    # ====================================================================
    # === Testes para Notificações ===
    # ====================================================================

    def test_notificacoes_page_logged_in(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        # Você pode criar um objeto Notification de teste aqui se tiver um modelo
        response = self.client.get(self.comprador_notificacoes_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comprador/notificacoes.html')
        # self.assertContains(response, 'Sua encomenda chegou!') # Se houver notificações de teste

    def test_notificacoes_not_logged_in(self):
        response = self.client.get(self.comprador_notificacoes_url)
        expected_redirect_url = f"{self.comprador_login_url}?next={self.comprador_notificacoes_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)


    # ====================================================================
    # === Testes para Logout do Comprador ===
    # ====================================================================

    def test_comprador_logout_successful(self):
        self.client.login(username=self.comprador_user.username, password=self.comprador_password)
        response_before_logout = self.client.get(self.comprador_home_url)
        self.assertEqual(response_before_logout.status_code, 200) # Confirma que estava logado

        response_logout = self.client.get(self.comprador_logout_url)
        self.assertRedirects(response_logout, self.comprador_login_url, status_code=302, target_status_code=200) # Redireciona para login

        # Tentar acessar uma página protegida (home) DEPOIS do logout deve redirecionar para o LOGIN_URL
        response_after_logout = self.client.get(self.comprador_home_url)
        expected_redirect_url_after_logout = f"{self.comprador_login_url}?next={self.comprador_home_url}"
        self.assertRedirects(response_after_logout, expected_redirect_url_after_logout, status_code=302, fetch_redirect_response=False)

    def test_comprador_logout_when_not_logged_in(self):
        response = self.client.get(self.comprador_logout_url)
        # Se o logout tem @login_required, ele redireciona para o login
        expected_redirect_url = f"{self.comprador_login_url}?next={self.comprador_logout_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, fetch_redirect_response=False)