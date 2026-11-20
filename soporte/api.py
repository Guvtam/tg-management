"""Recepción servidor-a-servidor de tickets enviados por TG Technology."""
import json
import logging
from hmac import compare_digest

from django import forms
from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from crm.models import Contacto, Empresa
from soporte.models import Ticket

logger = logging.getLogger(__name__)


class SolicitudAPIForm(forms.Form):
    referencia = forms.UUIDField()
    nombre = forms.CharField(max_length=120)
    correo = forms.EmailField()
    titulo = forms.CharField(max_length=200)
    descripcion = forms.CharField(max_length=5000)


def cliente_por_correo(correo):
    contactos = list(Contacto.objects.filter(
        email__iexact=correo, activo=True,
        empresa__tipo=Empresa.TipoEmpresa.CLIENTE,
        empresa__estado=Empresa.EstadoEmpresa.ACTIVA,
    ).select_related("empresa").order_by("pk")[:2])
    if len(contactos) == 1:
        return contactos[0].empresa, contactos[0]
    if contactos:
        return None, None
    empresas = list(Empresa.objects.filter(
        email__iexact=correo, tipo=Empresa.TipoEmpresa.CLIENTE,
        estado=Empresa.EstadoEmpresa.ACTIVA,
    )[:2])
    return (empresas[0], None) if len(empresas) == 1 else (None, None)


@csrf_exempt  # Autenticación servidor-a-servidor mediante token, no cookies.
@require_POST
def recibir_ticket_web(request):
    token = getattr(settings, "TG_SUPPORT_API_TOKEN", "")
    supplied = request.headers.get("Authorization", "")
    if not token or not supplied.startswith("Bearer ") or not compare_digest(supplied[7:], token):
        return JsonResponse({"error": "no_autorizado"}, status=401)
    if len(request.body) > 16384:
        return JsonResponse({"error": "solicitud_demasiado_grande"}, status=413)
    try:
        payload = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "json_invalido"}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"error": "datos_invalidos"}, status=400)
    form = SolicitudAPIForm(payload)
    if not form.is_valid():
        return JsonResponse({"error": "datos_invalidos", "campos": form.errors.get_json_data()}, status=422)
    data = form.cleaned_data
    try:
        with transaction.atomic():
            existente = Ticket.objects.filter(solicitud_web_id=data["referencia"]).first()
            if existente:
                if existente.correo_reportante.casefold() != data["correo"].casefold():
                    return JsonResponse({"error": "referencia_en_uso"}, status=409)
                return JsonResponse({"codigo": existente.codigo}, status=200)
            empresa, contacto = cliente_por_correo(data["correo"])
            if empresa is None:
                return JsonResponse({"error": "cliente_no_reconocido"}, status=422)
            ticket = Ticket.objects.create(
                solicitud_web_id=data["referencia"], empresa=empresa, contacto=contacto,
                nombre_reportante=data["nombre"], correo_reportante=data["correo"],
                titulo=data["titulo"], descripcion=data["descripcion"],
                canal=Ticket.Canal.FORMULARIO,
            )
    except IntegrityError:
        logger.warning("Conflicto al registrar ticket web")
        return JsonResponse({"error": "conflicto_temporal"}, status=409)
    return JsonResponse({"codigo": ticket.codigo}, status=201)
