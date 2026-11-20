"""Notificaciones de tickets de soporte creados desde el sitio web."""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape

logger = logging.getLogger(__name__)


def enviar_avisos_ticket(ticket_id):
    """Notifica una sola creación; los errores SMTP no afectan al ticket guardado."""
    from soporte.models import Ticket

    if not getattr(settings, "TG_SUPPORT_EMAIL_ENABLED", False):
        return

    ticket = Ticket.objects.select_related("empresa").get(pk=ticket_id)
    remitente = settings.DEFAULT_FROM_EMAIL
    codigo = ticket.codigo
    asunto = ticket.titulo
    cliente = ticket.nombre_reportante or "Cliente"

    if ticket.correo_reportante:
        texto = (
            f"Hola {cliente},\n\n"
            f"Recibimos tu solicitud de soporte.\n"
            f"Número de ticket: {codigo}\n"
            f"Asunto: {asunto}\n"
            f"Estado: Abierto\n\n"
            "Nuestro equipo revisará el caso y se pondrá en contacto contigo.\n"
            "Conserva el número de ticket para futuras consultas.\n\n"
            "TG Technology"
        )
        html = (
            '<div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;color:#0f172a">'
            '<div style="background:#102238;color:white;padding:22px;border-radius:12px 12px 0 0">'
            '<strong>TG TECHNOLOGY</strong><p style="margin-bottom:0">Confirmación de soporte</p></div>'
            '<div style="padding:26px;border:1px solid #e2e8f0">'
            f'<p>Hola {escape(cliente)},</p><p>Recibimos tu solicitud de soporte.</p>'
            f'<p style="background:#f0fdfa;padding:18px;border-radius:8px">'
            f'<strong>Número de ticket: {escape(codigo)}</strong></p>'
            f'<p><strong>Asunto:</strong> {escape(asunto)}<br><strong>Estado:</strong> Abierto</p>'
            '<p>Nuestro equipo revisará el caso y se pondrá en contacto contigo.</p>'
            '<p>Conserva el número de ticket para futuras consultas.</p>'
            '<p>Saludos,<br>TG Technology</p></div></div>'
        )
        try:
            email = EmailMultiAlternatives(
                f"[{codigo}] Confirmación de solicitud de soporte", texto,
                remitente, [ticket.correo_reportante],
            )
            email.attach_alternative(html, "text/html")
            email.send(fail_silently=False)
        except Exception:
            logger.exception("No se pudo enviar la confirmación del ticket %s", codigo)

    destino = getattr(settings, "TG_SUPPORT_NOTIFICATION_EMAIL", "")
    if destino:
        texto = (
            f"Nuevo ticket de soporte: {codigo}\n"
            f"Cliente: {ticket.empresa}\n"
            f"Reportado por: {cliente}\n"
            f"Correo: {ticket.correo_reportante}\n"
            f"Asunto: {asunto}\n"
            f"Categoría: {ticket.get_categoria_display()}\n"
            f"Prioridad: {ticket.get_prioridad_display()}\n"
            f"Descripción:\n{ticket.descripcion}\n\n"
            "Ingresa a TG Management para gestionar el caso."
        )
        try:
            EmailMultiAlternatives(
                f"[{codigo}] Nuevo ticket de soporte", texto,
                remitente, [destino],
            ).send(fail_silently=False)
        except Exception:
            logger.exception("No se pudo enviar el aviso interno del ticket %s", codigo)
