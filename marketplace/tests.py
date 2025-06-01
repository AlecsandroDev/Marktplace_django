from django.test import TestCase, Client
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

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