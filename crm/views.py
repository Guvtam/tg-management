from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from django.utils import timezone

from .forms import (
    ActividadForm,
    ContactoForm,
    EmpresaForm,
    OportunidadForm,
)
from .models import Actividad, Contacto, Empresa, Oportunidad


def empresa_lista(request):
    busqueda = request.GET.get("q", "").strip()

    empresas = Empresa.objects.all()

    if busqueda:
        empresas = empresas.filter(
            Q(razon_social__icontains=busqueda)
            | Q(nombre_fantasia__icontains=busqueda)
            | Q(rut__icontains=busqueda)
            | Q(comuna__icontains=busqueda)
            | Q(rubro__icontains=busqueda)
        )

    contexto = {
        "empresas": empresas,
        "busqueda": busqueda,
    }

    return render(
        request,
        "crm/empresa_lista.html",
        contexto,
    )


def empresa_crear(request):
    if request.method == "POST":
        form = EmpresaForm(request.POST)

        if form.is_valid():
            empresa = form.save(commit=False)

            if request.user.is_authenticated:
                empresa.creado_por = request.user

            empresa.save()

            messages.success(
                request,
                "La empresa fue creada correctamente.",
            )

            return redirect(
                "crm:empresa_detalle",
                pk=empresa.pk,
            )

    else:
        form = EmpresaForm()

    contexto = {
        "form": form,
        "titulo": "Nueva empresa",
        "texto_boton": "Guardar empresa",
    }

    return render(
        request,
        "crm/empresa_formulario.html",
        contexto,
    )


def empresa_detalle(request, pk):
    empresa = get_object_or_404(
        Empresa.objects.prefetch_related(
            "contactos",
            "oportunidades",
        ),
        pk=pk,
    )

    contexto = {
        "empresa": empresa,
    }

    return render(
        request,
        "crm/empresa_detalle.html",
        contexto,
    )


def empresa_editar(request, pk):
    empresa = get_object_or_404(
        Empresa,
        pk=pk,
    )

    if request.method == "POST":
        form = EmpresaForm(
            request.POST,
            instance=empresa,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "La empresa fue actualizada correctamente.",
            )

            return redirect(
                "crm:empresa_detalle",
                pk=empresa.pk,
            )

    else:
        form = EmpresaForm(
            instance=empresa,
        )

    contexto = {
        "form": form,
        "empresa": empresa,
        "titulo": "Editar empresa",
        "texto_boton": "Guardar cambios",
    }

    return render(
        request,
        "crm/empresa_formulario.html",
        contexto,
    )


def contacto_lista(request):
    busqueda = request.GET.get("q", "").strip()

    contactos = Contacto.objects.select_related(
        "empresa"
    ).all()

    if busqueda:
        contactos = contactos.filter(
            Q(nombres__icontains=busqueda)
            | Q(apellidos__icontains=busqueda)
            | Q(cargo__icontains=busqueda)
            | Q(email__icontains=busqueda)
            | Q(telefono__icontains=busqueda)
            | Q(empresa__razon_social__icontains=busqueda)
            | Q(empresa__nombre_fantasia__icontains=busqueda)
        )

    contexto = {
        "contactos": contactos,
        "busqueda": busqueda,
    }

    return render(
        request,
        "crm/contacto_lista.html",
        contexto,
    )


def contacto_crear(request):
    empresa_id = request.GET.get("empresa")

    if request.method == "POST":
        form = ContactoForm(request.POST)

        if form.is_valid():
            contacto = form.save()

            messages.success(
                request,
                "El contacto fue creado correctamente.",
            )

            return redirect(
                "crm:contacto_detalle",
                pk=contacto.pk,
            )

    else:
        datos_iniciales = {}

        if empresa_id:
            datos_iniciales["empresa"] = empresa_id

        form = ContactoForm(
            initial=datos_iniciales,
        )

    contexto = {
        "form": form,
        "titulo": "Nuevo contacto",
        "texto_boton": "Guardar contacto",
    }

    return render(
        request,
        "crm/contacto_formulario.html",
        contexto,
    )


def contacto_detalle(request, pk):
    contacto = get_object_or_404(
        Contacto.objects.select_related(
            "empresa"
        ),
        pk=pk,
    )

    contexto = {
        "contacto": contacto,
    }

    return render(
        request,
        "crm/contacto_detalle.html",
        contexto,
    )


def contacto_editar(request, pk):
    contacto = get_object_or_404(
        Contacto,
        pk=pk,
    )

    if request.method == "POST":
        form = ContactoForm(
            request.POST,
            instance=contacto,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "El contacto fue actualizado correctamente.",
            )

            return redirect(
                "crm:contacto_detalle",
                pk=contacto.pk,
            )

    else:
        form = ContactoForm(
            instance=contacto,
        )

    contexto = {
        "form": form,
        "contacto": contacto,
        "titulo": "Editar contacto",
        "texto_boton": "Guardar cambios",
    }

    return render(
        request,
        "crm/contacto_formulario.html",
        contexto,
    )


def oportunidad_lista(request):
    busqueda = request.GET.get("q", "").strip()
    etapa = request.GET.get("etapa", "").strip()
    prioridad = request.GET.get("prioridad", "").strip()

    oportunidades = Oportunidad.objects.select_related(
        "empresa",
        "contacto",
        "responsable",
    ).all()

    if busqueda:
        oportunidades = oportunidades.filter(
            Q(titulo__icontains=busqueda)
            | Q(empresa__razon_social__icontains=busqueda)
            | Q(empresa__nombre_fantasia__icontains=busqueda)
            | Q(contacto__nombres__icontains=busqueda)
            | Q(contacto__apellidos__icontains=busqueda)
            | Q(servicio_interes__icontains=busqueda)
        )

    if etapa:
        oportunidades = oportunidades.filter(
            etapa=etapa,
        )

    if prioridad:
        oportunidades = oportunidades.filter(
            prioridad=prioridad,
        )

    contexto = {
        "oportunidades": oportunidades,
        "busqueda": busqueda,
        "etapa_seleccionada": etapa,
        "prioridad_seleccionada": prioridad,
        "etapas": Oportunidad.Etapa.choices,
        "prioridades": Oportunidad.Prioridad.choices,
    }

    return render(
        request,
        "crm/oportunidad_lista.html",
        contexto,
    )


def oportunidad_crear(request):
    empresa_id = request.GET.get("empresa")

    if request.method == "POST":
        form = OportunidadForm(request.POST)

        if form.is_valid():
            oportunidad = form.save()

            messages.success(
                request,
                "La oportunidad fue creada correctamente.",
            )

            return redirect(
                "crm:oportunidad_detalle",
                pk=oportunidad.pk,
            )

    else:
        datos_iniciales = {}

        if empresa_id:
            datos_iniciales["empresa"] = empresa_id

        form = OportunidadForm(
            initial=datos_iniciales,
        )

    contexto = {
        "form": form,
        "titulo": "Nueva oportunidad",
        "texto_boton": "Guardar oportunidad",
    }

    return render(
        request,
        "crm/oportunidad_formulario.html",
        contexto,
    )


def oportunidad_detalle(request, pk):
    oportunidad = get_object_or_404(
        Oportunidad.objects.select_related(
            "empresa",
            "contacto",
            "responsable",
        ).prefetch_related(
            "actividades",
            "cotizaciones",
        ),
        pk=pk,
    )

    contexto = {
        "oportunidad": oportunidad,
    }

    return render(
        request,
        "crm/oportunidad_detalle.html",
        contexto,
    )


def oportunidad_editar(request, pk):
    oportunidad = get_object_or_404(
        Oportunidad,
        pk=pk,
    )

    if request.method == "POST":
        form = OportunidadForm(
            request.POST,
            instance=oportunidad,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "La oportunidad fue actualizada correctamente.",
            )

            return redirect(
                "crm:oportunidad_detalle",
                pk=oportunidad.pk,
            )

    else:
        form = OportunidadForm(
            instance=oportunidad,
        )

    contexto = {
        "form": form,
        "oportunidad": oportunidad,
        "titulo": "Editar oportunidad",
        "texto_boton": "Guardar cambios",
    }

    return render(
        request,
        "crm/oportunidad_formulario.html",
        contexto,
    )


def actividad_lista(request):
    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "").strip()
    tipo = request.GET.get("tipo", "").strip()

    actividades = Actividad.objects.select_related(
        "oportunidad",
        "oportunidad__empresa",
        "responsable",
    ).all()

    if busqueda:
        actividades = actividades.filter(
            Q(asunto__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
            | Q(resultado__icontains=busqueda)
            | Q(oportunidad__titulo__icontains=busqueda)
            | Q(
                oportunidad__empresa__razon_social__icontains=busqueda
            )
            | Q(
                oportunidad__empresa__nombre_fantasia__icontains=busqueda
            )
        )

    if estado:
        actividades = actividades.filter(
            estado=estado,
        )

    if tipo:
        actividades = actividades.filter(
            tipo=tipo,
        )

    actividades = actividades.order_by(
        "fecha_programada"
    )

    contexto = {
        "actividades": actividades,
        "busqueda": busqueda,
        "estado_seleccionado": estado,
        "tipo_seleccionado": tipo,
        "estados": Actividad.EstadoActividad.choices,
        "tipos": Actividad.TipoActividad.choices,
        "ahora": timezone.now(),
    }

    return render(
        request,
        "crm/actividad_lista.html",
        contexto,
    )


def actividad_crear(request):
    oportunidad_id = request.GET.get("oportunidad")

    if request.method == "POST":
        form = ActividadForm(request.POST)

        if form.is_valid():
            actividad = form.save(commit=False)

            if (
                not actividad.responsable
                and request.user.is_authenticated
            ):
                actividad.responsable = request.user

            actividad.save()

            messages.success(
                request,
                "La actividad fue creada correctamente.",
            )

            return redirect(
                "crm:actividad_detalle",
                pk=actividad.pk,
            )

    else:
        datos_iniciales = {
            "fecha_programada": timezone.localtime().strftime(
                "%Y-%m-%dT%H:%M"
            ),
        }

        if oportunidad_id:
            datos_iniciales["oportunidad"] = oportunidad_id

        if request.user.is_authenticated:
            datos_iniciales["responsable"] = request.user.pk

        form = ActividadForm(
            initial=datos_iniciales,
        )

    contexto = {
        "form": form,
        "titulo": "Nueva actividad",
        "texto_boton": "Guardar actividad",
    }

    return render(
        request,
        "crm/actividad_formulario.html",
        contexto,
    )


def actividad_detalle(request, pk):
    actividad = get_object_or_404(
        Actividad.objects.select_related(
            "oportunidad",
            "oportunidad__empresa",
            "oportunidad__contacto",
            "responsable",
        ),
        pk=pk,
    )

    contexto = {
        "actividad": actividad,
    }

    return render(
        request,
        "crm/actividad_detalle.html",
        contexto,
    )


def actividad_editar(request, pk):
    actividad = get_object_or_404(
        Actividad,
        pk=pk,
    )

    if request.method == "POST":
        form = ActividadForm(
            request.POST,
            instance=actividad,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "La actividad fue actualizada correctamente.",
            )

            return redirect(
                "crm:actividad_detalle",
                pk=actividad.pk,
            )

    else:
        form = ActividadForm(
            instance=actividad,
        )

    contexto = {
        "form": form,
        "actividad": actividad,
        "titulo": "Editar actividad",
        "texto_boton": "Guardar cambios",
    }

    return render(
        request,
        "crm/actividad_formulario.html",
        contexto,
    )


def actividad_completar(request, pk):
    actividad = get_object_or_404(
        Actividad,
        pk=pk,
    )

    if request.method == "POST":
        actividad.estado = (
            Actividad.EstadoActividad.COMPLETADA
        )

        actividad.save(
            update_fields=[
                "estado",
                "fecha_actualizacion",
            ]
        )

        messages.success(
            request,
            "La actividad fue marcada como completada.",
        )

    return redirect(
        "crm:actividad_detalle",
        pk=actividad.pk,
    )