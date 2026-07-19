from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from crm.models import Empresa
from proyectos.models import Proyecto

from .models import EncuestaSatisfaccion


class EncuestaSatisfaccionTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="tamara", password="prueba-segura-123"
        )
        self.empresa = Empresa.objects.create(razon_social="Cliente Demo SpA")
        self.proyecto = Proyecto.objects.create(
            nombre="Dashboard Power BI", empresa=self.empresa
        )
        self.encuesta = EncuestaSatisfaccion.objects.create(
            proyecto=self.proyecto,
            empresa=self.empresa,
            creado_por=self.usuario,
        )

    def test_empresa_se_sincroniza_con_proyecto(self):
        self.assertEqual(self.encuesta.empresa_id, self.proyecto.empresa_id)

    def test_enlace_publico_no_requiere_login(self):
        respuesta = self.client.get(
            reverse("encuestas:responder", kwargs={"token": self.encuesta.token})
        )
        self.assertEqual(respuesta.status_code, 200)

    def test_respuesta_valida_cierra_encuesta(self):
        respuesta = self.client.post(
            reverse("encuestas:responder", kwargs={"token": self.encuesta.token}),
            {
                "satisfaccion_general": 5,
                "calidad_solucion": 5,
                "cumplimiento_expectativas": "completamente",
                "comunicacion": 4,
                "cumplimiento_plazos": 4,
                "recomendacion": 10,
                "aspectos_valorados": "La claridad del trabajo.",
                "aspectos_mejora": "Nada por ahora.",
                "testimonio": "Excelente servicio.",
                "autoriza_testimonio": "on",
            },
        )
        self.assertEqual(respuesta.status_code, 302)
        self.encuesta.refresh_from_db()
        self.assertEqual(self.encuesta.estado, EncuestaSatisfaccion.Estado.RESPONDIDA)
        self.assertIsNotNone(self.encuesta.fecha_respuesta)

    def test_encuesta_respondida_no_acepta_otra_respuesta(self):
        self.encuesta.estado = EncuestaSatisfaccion.Estado.RESPONDIDA
        self.encuesta.fecha_respuesta = timezone.now()
        self.encuesta.save()
        respuesta = self.client.get(
            reverse("encuestas:responder", kwargs={"token": self.encuesta.token})
        )
        self.assertContains(respuesta, "ya fue respondida")

    def test_encuesta_vencida_no_esta_disponible(self):
        self.encuesta.fecha_vencimiento = timezone.localdate() - timedelta(days=1)
        self.encuesta.save()
        respuesta = self.client.get(
            reverse("encuestas:responder", kwargs={"token": self.encuesta.token})
        )
        self.assertEqual(respuesta.status_code, 410)
