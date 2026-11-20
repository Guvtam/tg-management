from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import InteraccionTicketForm, TicketEstadoForm, TicketForm
from .models import Ticket


def ticket_lista(request):
    tickets = Ticket.objects.select_related(
        "empresa",
        "contacto",
        "proyecto",
        "responsable",
    )

    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "").strip()
    prioridad = request.GET.get("prioridad", "").strip()
    solo_vencidos = request.GET.get("vencidos", "").strip()

    if busqueda:
        tickets = tickets.filter(
            Q(titulo__icontains=busqueda)
            | Q(codigo__icontains=busqueda)
            | Q(empresa__razon_social__icontains=busqueda)
            | Q(empresa__nombre_fantasia__icontains=busqueda)
            | Q(nombre_reportante__icontains=busqueda)
            | Q(correo_reportante__icontains=busqueda)
        )

    if estado:
        tickets = tickets.filter(estado=estado)

    if prioridad:
        tickets = tickets.filter(prioridad=prioridad)

    if solo_vencidos:
        tickets = [t for t in tickets if t.esta_vencido]

    abiertos = Ticket.objects.exclude(
        estado__in=[Ticket.Estado.RESUELTO, Ticket.Estado.CERRADO]
    )

    context = {
        "tickets": tickets,
        "estados": Ticket.Estado.choices,
        "prioridades": Ticket.Prioridad.choices,
        "estado_seleccionado": estado,
        "prioridad_seleccionada": prioridad,
        "busqueda": busqueda,
        "solo_vencidos": solo_vencidos,
        "total_abiertos": abiertos.count(),
        "total_vencidos": len([t for t in abiertos if t.esta_vencido]),
    }

    return render(request, "soporte/ticket_lista.html", context)


def ticket_crear(request):
    if request.method == "POST":
        form = TicketForm(request.POST)

        if form.is_valid():
            ticket = form.save(commit=False)

            if request.user.is_authenticated:
                ticket.responsable = ticket.responsable or request.user

            ticket.save()

            messages.success(request, "Ticket registrado correctamente.")

            return redirect("soporte:ticket_detalle", pk=ticket.pk)
    else:
        form = TicketForm()

    context = {
        "form": form,
        "titulo": "Nuevo ticket",
        "boton": "Registrar ticket",
    }

    return render(request, "soporte/ticket_form.html", context)


def ticket_editar(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)

    if request.method == "POST":
        form = TicketForm(request.POST, instance=ticket)

        if form.is_valid():
            form.save()

            messages.success(request, "Ticket actualizado correctamente.")

            return redirect("soporte:ticket_detalle", pk=ticket.pk)
    else:
        form = TicketForm(instance=ticket)

    context = {
        "form": form,
        "ticket": ticket,
        "titulo": "Editar ticket",
        "boton": "Guardar cambios",
    }

    return render(request, "soporte/ticket_form.html", context)


def ticket_detalle(request, pk):
    ticket = get_object_or_404(
        Ticket.objects.select_related("empresa", "contacto", "proyecto", "responsable"),
        pk=pk,
    )

    interacciones = ticket.interacciones.select_related("autor")

    if request.method == "POST":
        if "agregar_interaccion" in request.POST:
            interaccion_form = InteraccionTicketForm(request.POST)

            if interaccion_form.is_valid():
                interaccion = interaccion_form.save(commit=False)
                interaccion.ticket = ticket

                if request.user.is_authenticated:
                    interaccion.autor = request.user

                interaccion.save()

                if not ticket.fecha_primera_respuesta and interaccion.tipo == "respuesta_cliente":
                    ticket.fecha_primera_respuesta = timezone.now()
                    ticket.save(update_fields=["fecha_primera_respuesta"])

                messages.success(request, "Interacción registrada.")

                return redirect("soporte:ticket_detalle", pk=ticket.pk)

            estado_form = TicketEstadoForm(instance=ticket)

        else:
            estado_form = TicketEstadoForm(request.POST, instance=ticket)

            if estado_form.is_valid():
                ticket_actualizado = estado_form.save(commit=False)

                if (
                    ticket_actualizado.estado == Ticket.Estado.RESUELTO
                    and not ticket.fecha_resolucion
                ):
                    ticket_actualizado.fecha_resolucion = timezone.now()

                ticket_actualizado.save()

                messages.success(request, "Estado del ticket actualizado.")

                return redirect("soporte:ticket_detalle", pk=ticket.pk)

            interaccion_form = InteraccionTicketForm()
    else:
        estado_form = TicketEstadoForm(instance=ticket)
        interaccion_form = InteraccionTicketForm()

    context = {
        "ticket": ticket,
        "interacciones": interacciones,
        "estado_form": estado_form,
        "interaccion_form": interaccion_form,
    }

    return render(request, "soporte/ticket_detalle.html", context)


def ticket_eliminar(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)

    if request.method == "POST":
        ticket.delete()

        messages.success(request, "Ticket eliminado correctamente.")

    return redirect("soporte:ticket_lista")
