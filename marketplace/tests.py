from django.test import TestCase, Client
from django.urls import reverse

class MarketplaceTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_status_code_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)