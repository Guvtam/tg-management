import json
import sys

from django import forms
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from crm.models import Contacto, Empresa
from soporte.models import Ticket


class SolicitudWebForm(forms.Form):
    referencia = forms.UUIDField()
    nombre = forms.CharField(max_length=120)
    correo = forms.EmailField()
    titulo = forms.CharField(max_length=200)
    descripcion = forms.CharField(max_length=5000)


def cliente_del_ticket(correo):
    contactos = list(
        Contacto.objects.filter(
            email__iexact=correo,
            activo=True,
            empresa__tipo=Empresa.TipoEmpresa.CLIENTE,
            empresa__estado=Empresa.EstadoEmpresa.ACTIVA,
        ).order_by("pk")[:2]
    )
    if len(contactos) == 1:
        return contactos[0].empresa, contactos[0]
    if contactos:
        return None, None

    empresas = list(
        Empresa.objects.filter(
            email__iexact=correo,
            tipo=Empresa.TipoEmpresa.CLIENTE,
            estado=Empresa.EstadoEmpresa.ACTIVA,
        )[:2]
    )
    return (empresas[0], None) if len(empresas) == 1 else (None, None)


class Command(BaseCommand):
    help = "Registra una solicitud web de soporte recibida como JSON por stdin."

    def handle(self, *args, **options):
        try:
            payload = json.load(sys.stdin)
        except ValueError as exc:
            raise CommandError("Solicitud inválida") from exc
        if not isinstance(payload, dict):
            raise CommandError("Solicitud inválida")
        form = SolicitudWebForm(payload)
        if not form.is_valid():
            raise CommandError("Solicitud inválida")

        data = form.cleaned_data
        with transaction.atomic():
            empresa, contacto = cliente_del_ticket(data["correo"])
            if empresa is None:
                self.stdout.write(json.dumps({"error": "cliente_no_reconocido"}))
                return
            ticket, _ = Ticket.objects.get_or_create(
                solicitud_web_id=data["referencia"],
                defaults={
                    "empresa": empresa,
                    "contacto": contacto,
                    "nombre_reportante": data["nombre"],
                    "correo_reportante": data["correo"],
                    "titulo": data["titulo"],
                    "descripcion": data["descripcion"],
                    "canal": Ticket.Canal.FORMULARIO,
                },
            )
        self.stdout.write(json.dumps({"codigo": ticket.codigo}))
