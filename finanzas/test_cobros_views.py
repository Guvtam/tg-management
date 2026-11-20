from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CobrosDashboardTests(TestCase):
    def setUp(self):
        self.url = reverse("finanzas:bandeja_cobros")

    def test_anonymous_user_cannot_access_dashboard(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_nonstaff_user_cannot_access_dashboard(self):
        user = get_user_model().objects.create_user(username="operador", password="clave-de-prueba")
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)

    def test_staff_user_can_view_dashboard(self):
        user = get_user_model().objects.create_user(username="administrador", password="clave-de-prueba", is_staff=True)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bandeja de cobros")
