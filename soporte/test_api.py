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
            "correo": "ana@example.com", "categoria": "incidente", "impacto": "alto", "titulo": "Problema de acceso",
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
        self.assertEqual(ticket.categoria, Ticket.Categoria.INCIDENTE)
        self.assertEqual(ticket.prioridad, Ticket.Prioridad.ALTA)
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


    @override_settings(
        TG_SUPPORT_EMAIL_ENABLED=True,
        TG_SUPPORT_NOTIFICATION_EMAIL="soporte-interno@example.com",
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="no-reply@example.com",
    )
    def test_new_ticket_sends_customer_and_internal_email(self):
        from django.core import mail

        with self.captureOnCommitCallbacks(execute=True):
            response = self.enviar()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(response.json()["codigo"], mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["ana@example.com"])
        self.assertEqual(mail.outbox[1].to, ["soporte-interno@example.com"])
        self.assertEqual(len(mail.outbox[0].alternatives), 1)

        with self.captureOnCommitCallbacks(execute=True):
            retry = self.enviar()
        self.assertEqual(retry.status_code, 200)
        self.assertEqual(len(mail.outbox), 2)

    @override_settings(
        TG_SUPPORT_EMAIL_ENABLED=False,
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_notifications_disabled_by_default(self):
        from django.core import mail

        with self.captureOnCommitCallbacks(execute=True):
            response = self.enviar()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 0)


    @override_settings(
        TG_SUPPORT_EMAIL_ENABLED=True,
        TG_SUPPORT_NOTIFICATION_EMAIL="soporte-interno@example.com",
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="no-reply@example.com",
    )
    def test_email_failure_does_not_rollback_ticket(self):
        from unittest.mock import patch

        with patch("soporte.notifications.EmailMultiAlternatives.send", side_effect=OSError("SMTP unavailable")):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.enviar()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ticket.objects.count(), 1)
        self.assertEqual(response.json()["codigo"], Ticket.objects.get().codigo)

    def test_invalid_category_is_rejected_without_creating_ticket(self):
        payload = {**self.payload, "categoria": "no_valida"}
        response = self.enviar(payload)
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Ticket.objects.exists())

    def test_rejects_payload_over_size_limit(self):
        payload = {**self.payload, "descripcion": "a" * 17000}
        response = self.enviar(payload)
        self.assertEqual(response.status_code, 413)
        self.assertFalse(Ticket.objects.exists())
