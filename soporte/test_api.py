import json
from uuid import uuid4

from django.test import TestCase, override_settings
from django.urls import reverse

from crm.models import Contacto, Empresa
from soporte.models import Ticket


@override_settings(TG_SUPPORT_API_TOKEN="test-secret")
class SupportAPITests(TestCase):
    def setUp(self):
        self.url = reverse("soporte:api_tickets")
        self.empresa = Empresa.objects.create(
            razon_social="Cliente de prueba SpA",
            tipo=Empresa.TipoEmpresa.CLIENTE,
            estado=Empresa.EstadoEmpresa.ACTIVA,
        )
        self.contacto = Contacto.objects.create(
            empresa=self.empresa, nombres="Ana", apellidos="Prueba",
            email="ana@example.com", activo=True,
        )
        self.payload = {
            "referencia": str(uuid4()), "nombre": "Ana Prueba",
            "correo": "ana@example.com", "titulo": "Problema de acceso",
            "descripcion": "No puedo acceder al sistema.",
        }

    def enviar(self, payload=None, token="test-secret"):
        return self.client.post(
            self.url, data=json.dumps(self.payload if payload is None else payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

    def test_missing_token_rejected(self):
        response = self.client.post(self.url, data="{}", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_wrong_token_rejected(self):
        self.assertEqual(self.enviar(token="wrong").status_code, 401)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_invalid_payload_rejected(self):
        self.assertEqual(self.enviar({}).status_code, 422)

    def test_creates_ticket_linked_to_customer(self):
        response = self.enviar()
        self.assertEqual(response.status_code, 201)
        ticket = Ticket.objects.get()
        self.assertEqual(response.json()["codigo"], ticket.codigo)
        self.assertTrue(ticket.codigo.startswith("TCK-"))
        self.assertEqual(ticket.empresa, self.empresa)
        self.assertEqual(ticket.contacto, self.contacto)
        self.assertEqual(ticket.estado, Ticket.Estado.ABIERTO)
        self.assertEqual(ticket.canal, Ticket.Canal.FORMULARIO)
        self.assertEqual(ticket.descripcion, self.payload["descripcion"])

    def test_repeated_reference_returns_same_ticket(self):
        first = self.enviar()
        second = self.enviar()
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json()["codigo"], second.json()["codigo"])
        self.assertEqual(Ticket.objects.count(), 1)

    def test_unknown_customer_does_not_create_ticket(self):
        payload = {**self.payload, "correo": "desconocido@example.com"}
        response = self.enviar(payload)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"], "cliente_no_reconocido")
        self.assertFalse(Ticket.objects.exists())

    def test_duplicate_reference_different_email_is_rejected(self):
        self.enviar()
        payload = {**self.payload, "correo": "otro@example.com"}
        response = self.enviar(payload)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_inactive_customer_is_rejected(self):
        self.empresa.estado = Empresa.EstadoEmpresa.INACTIVA
        self.empresa.save(update_fields=["estado"])
        response = self.enviar()
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Ticket.objects.exists())
