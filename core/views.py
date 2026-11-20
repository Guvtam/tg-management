import logging
import sqlite3
from contextlib import closing
from datetime import UTC
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, OperationalError, transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST

from crm.models import Actividad, Contacto, Empresa, Oportunidad


def dashboard(request):
    contexto = {
        "total_empresas": Empresa.objects.count(),
        "total_contactos": Contacto.objects.count(),
        "total_oportunidades": Oportunidad.objects.count(),
        "oportunidades_ganadas": Oportunidad.objects.filter(
            etapa=Oportunidad.Etapa.GANADA
        ).count(),
        "actividades_pendientes": Actividad.objects.filter(
            estado=Actividad.EstadoActividad.PENDIENTE
        ).count(),
        "ultimas_oportunidades": Oportunidad.objects.select_related(
            "empresa",
            "responsable",
        )[:5],
    }

    return render(request, "core/dashboard.html", contexto)

logger = logging.getLogger(__name__)
WEB_SERVICES = {
    "web": "Página web",
    "system": "Sistema web",
    "data": "Análisis de datos",
    "ecommerce": "Tienda online",
    "other": "Otra solución",
}


def leer_solicitudes_web(pk=None):
    source = settings.TG_TECHNOLOGY_DB
    if not source:
        raise OSError("Base de solicitudes web sin configurar")

    uri = Path(source).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True, timeout=2)) as connection:
        connection.row_factory = sqlite3.Row
        query = """
            SELECT id, name, company, email, phone, service, budget, message, created_at, is_contacted
            FROM core_contactrequest
        """
        if pk is not None:
            return connection.execute(query + " WHERE id = ?", (pk,)).fetchone()
        return connection.execute(query + " ORDER BY created_at DESC, id DESC").fetchall()


@login_required
def solicitudes_web(request):
    unavailable = False
    try:
        rows = leer_solicitudes_web()
    except (OSError, sqlite3.Error):
        logger.warning("No se pudieron consultar las solicitudes web")
        rows = []
        unavailable = True

    page = Paginator(rows, 20).get_page(request.GET.get("page"))
    oportunidades = dict(Oportunidad.objects.filter(
        solicitud_web_id__in=[row["id"] for row in page],
    ).values_list("solicitud_web_id", "pk"))
    contacts = []
    for row in page:
        contact = presentar_solicitud_web(row)
        contact["oportunidad_id"] = oportunidades.get(row["id"])
        contacts.append(contact)

    return render(request, "core/solicitudes_web.html", {
        "contacts": contacts,
        "page_obj": page,
        "unavailable": unavailable,
    })


def presentar_solicitud_web(row):
    contact = dict(row)
    contact["service"] = WEB_SERVICES.get(row["service"], row["service"])
    date = parse_datetime(row["created_at"])
    if date and timezone.is_naive(date):
        date = timezone.make_aware(date, UTC)
    contact["created_at"] = date
    return contact


@login_required
def solicitud_web_detalle(request, pk):
    try:
        row = leer_solicitudes_web(pk)
    except (OSError, sqlite3.Error):
        messages.error(request, "No se pudo leer la solicitud web. Intenta nuevamente.")
        return redirect("core:solicitudes_web")
    if row is None:
        raise Http404("Solicitud web no encontrada")

    contact = presentar_solicitud_web(row)
    oportunidad = Oportunidad.objects.filter(solicitud_web_id=pk).first()
    return render(request, "core/solicitud_web_detalle.html", {
        "contact": contact,
        "oportunidad": oportunidad,
    })


@transaction.atomic
def registrar_oportunidad_web(solicitud, usuario):
    oportunidad = Oportunidad.objects.filter(solicitud_web_id=solicitud["id"]).first()
    if oportunidad:
        return oportunidad

    correo = solicitud["email"].strip()
    negocio = solicitud["company"].strip()
    nombre = solicitud["name"].strip()
    contactos = Contacto.objects.select_related("empresa").filter(email__iexact=correo)
    if negocio:
        contacto = contactos.filter(
            Q(empresa__razon_social__iexact=negocio) | Q(empresa__nombre_fantasia__iexact=negocio)
        ).order_by("pk").first()
    else:
        contacto = None
    if contacto is None:
        contacto = contactos.order_by("pk").first()

    if contacto is None:
        empresa = None
        if negocio:
            empresa = Empresa.objects.filter(
                Q(razon_social__iexact=negocio) | Q(nombre_fantasia__iexact=negocio),
                tipo__in=[Empresa.TipoEmpresa.PROSPECTO, Empresa.TipoEmpresa.CLIENTE],
            ).order_by("pk").first()
        if empresa is None:
            empresa = Empresa.objects.create(razon_social=negocio or nombre, creado_por=usuario)
        nombre_contacto, _, resto = nombre.rpartition(" ")
        contacto = Contacto.objects.create(
            empresa=empresa,
            nombres=(nombre_contacto or nombre)[:100],
            apellidos=resto[:100] if nombre_contacto else "",
            email=correo,
            telefono=solicitud["phone"],
        )

    servicio = WEB_SERVICES.get(solicitud["service"], solicitud["service"])
    return Oportunidad.objects.create(
        solicitud_web_id=solicitud["id"],
        titulo=f"{servicio} · {contacto.empresa}"[:200],
        empresa=contacto.empresa,
        contacto=contacto,
        servicio_interes=servicio,
        descripcion=solicitud["message"],
        responsable=usuario,
    )


@login_required
@require_POST
def convertir_solicitud_web(request, pk):
    try:
        solicitud = leer_solicitudes_web(pk)
    except (OSError, sqlite3.Error):
        messages.error(request, "No se pudo leer la solicitud web. Intenta nuevamente.")
        return redirect("core:solicitudes_web")
    if solicitud is None:
        raise Http404("Solicitud web no encontrada")

    try:
        oportunidad = registrar_oportunidad_web(solicitud, request.user)
    except (IntegrityError, OperationalError):
        oportunidad = Oportunidad.objects.filter(solicitud_web_id=pk).first()
        if oportunidad is None:
            logger.exception("No se pudo convertir la solicitud web %s", pk)
            messages.error(request, "No se pudo convertir la solicitud. Intenta nuevamente.")
            return redirect("core:solicitudes_web")
    return redirect("crm:oportunidad_detalle", pk=oportunidad.pk)
