from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import Resolver404, resolve, reverse

from crm.models import Empresa


class InternalAccessTests(TestCase):
    def test_anonymous_users_cannot_read_internal_pages(self):
        paths = [
            "/",
            "/crm/empresas/",
            "/cotizaciones/",
            "/proyectos/",
            "/finanzas/",
            "/soporte/tickets/",
            "/encuestas/",
            "/modalidades-pago/",
        ]
        for path in paths:
            with self.subTest(path=path):
                resolve(path)
                response = self.client.get(path)
                self.assertRedirects(
                    response,
                    f"{resolve_url(settings.LOGIN_URL)}?next={path}",
                    fetch_redirect_response=False,
                )

    def test_anonymous_users_cannot_create_crm_records(self):
        path = reverse("crm:empresa_crear")
        response = self.client.post(path, {"razon_social": "Empresa de prueba"})

        self.assertRedirects(
            response,
            f"{resolve_url(settings.LOGIN_URL)}?next={path}",
            fetch_redirect_response=False,
        )

        self.assertFalse(Empresa.objects.exists())

    def test_anonymous_users_cannot_access_project_documents(self):
        for name in ("documento_visualizar", "documento_descargar"):
            with self.subTest(name=name):
                path = reverse(f"proyectos:{name}", args=[1])
                response = self.client.get(path)
                self.assertRedirects(
                    response,
                    f"{resolve_url(settings.LOGIN_URL)}?next={path}",
                    fetch_redirect_response=False,
                )

    def test_media_has_no_direct_route(self):
        with self.assertRaises(Resolver404):
            resolve("/media/documentos/prueba.pdf")

    def test_login_is_public_and_authenticated_user_reaches_dashboard(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        user = get_user_model().objects.create_user(username="operador")
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("core:dashboard")).status_code, 200)
