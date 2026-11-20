from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cotizaciones.models import Cotizacion


class EstadoCotizacionTests(TestCase):
    def setUp(self):
        self.url = reverse("cotizaciones:cotizacion_cambiar_estado", args=[999999])

    def test_anonymous_cannot_change_status(self):
        response = self.client.post(self.url, {"estado": "aprobada"})
        self.assertEqual(response.status_code, 302)

    def test_nonstaff_cannot_change_status(self):
        user = get_user_model().objects.create_user(username="operador_estado", password="clave")
        self.client.force_login(user)
        response = self.client.post(self.url, {"estado": "aprobada"})
        self.assertNotEqual(response.status_code, 200)

    def test_get_does_not_change_status(self):
        user = get_user_model().objects.create_user(username="admin_estado", password="clave", is_staff=True)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_invalid_status_does_not_write(self):
        user = get_user_model().objects.create_user(username="admin_estado2", password="clave", is_staff=True)
        self.client.force_login(user)
        response = self.client.post(self.url, {"estado": "inventado"})
        self.assertRedirects(response, reverse("cotizaciones:cotizacion_lista"))
