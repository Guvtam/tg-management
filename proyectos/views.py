from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from cotizaciones.models import Cotizacion

from .forms import ActividadProyectoForm, ProyectoForm
from .models import ActividadProyecto, Proyecto



def proyecto_lista(request):
    proyectos = Proyecto.objects.select_related(
        "empresa",
        "cotizacion",
        "responsable",
    )

    estado = request.GET.get("estado", "").strip()
    busqueda = request.GET.get("q", "").strip()

    if estado:
        proyectos = proyectos.filter(estado=estado)

    if busqueda:
        proyectos = proyectos.filter(
            Q(nombre__icontains=busqueda)
            | Q(codigo__icontains=busqueda)
            | Q(empresa__nombre__icontains=busqueda)
        )

    context = {
        "proyectos": proyectos,
        "estados": Proyecto.Estado.choices,
        "estado_seleccionado": estado,
        "busqueda": busqueda,
    }

    return render(
        request,
        "proyectos/proyecto_lista.html",
        context,
    )


def proyecto_crear(request):
    if request.method == "POST":
        form = ProyectoForm(request.POST)

        if form.is_valid():
            proyecto = form.save(commit=False)

            if request.user.is_authenticated:
                proyecto.creado_por = request.user

            proyecto.save()

            messages.success(
                request,
                "Proyecto creado correctamente.",
            )

            return redirect(
                "proyectos:proyecto_detalle",
                pk=proyecto.pk,
            )
    else:
        form = ProyectoForm()

    context = {
        "form": form,
        "titulo": "Nuevo proyecto",
        "boton": "Crear proyecto",
    }

    return render(
        request,
        "proyectos/proyecto_form.html",
        context,
    )

def proyecto_detalle(request, pk):
    proyecto = get_object_or_404(
        Proyecto.objects.select_related(
            "empresa",
            "cotizacion",
            "responsable",
            "creado_por",
        ),
        pk=pk,
    )

    actividades = (
        proyecto.actividades
        .select_related("responsable")
        .all()
    )

    total_actividades = actividades.count()

    actividades_completadas = actividades.filter(
        estado=ActividadProyecto.Estado.COMPLETADA
    ).count()

    if total_actividades > 0:
        avance_actividades = round(
            actividades_completadas * 100 / total_actividades
        )
    else:
        avance_actividades = 0

    context = {
        "proyecto": proyecto,
        "actividades": actividades,
        "total_actividades": total_actividades,
        "actividades_completadas": actividades_completadas,
        "avance_actividades": avance_actividades,
    }

    return render(
        request,
        "proyectos/proyecto_detalle.html",
        context,
    )


def proyecto_editar(request, pk):
    proyecto = get_object_or_404(
        Proyecto,
        pk=pk,
    )

    if request.method == "POST":
        form = ProyectoForm(
            request.POST,
            instance=proyecto,
        )

        if form.is_valid():
            proyecto = form.save()

            messages.success(
                request,
                "Proyecto actualizado correctamente.",
            )

            return redirect(
                "proyectos:proyecto_detalle",
                pk=proyecto.pk,
            )
    else:
        form = ProyectoForm(
            instance=proyecto,
        )

    context = {
        "form": form,
        "proyecto": proyecto,
        "titulo": "Editar proyecto",
        "boton": "Guardar cambios",
    }

    return render(
        request,
        "proyectos/proyecto_form.html",
        context,
    )

def actividad_crear(request, proyecto_pk):
    proyecto = get_object_or_404(
        Proyecto,
        pk=proyecto_pk,
    )

    if request.method == "POST":
        form = ActividadProyectoForm(request.POST)

        if form.is_valid():
            actividad = form.save(commit=False)
            actividad.proyecto = proyecto
            actividad.save()

            messages.success(
                request,
                "Actividad agregada correctamente.",
            )

            return redirect(
                "proyectos:proyecto_detalle",
                pk=proyecto.pk,
            )
    else:
        form = ActividadProyectoForm()

    context = {
        "form": form,
        "proyecto": proyecto,
        "titulo": "Nueva actividad",
        "boton": "Agregar actividad",
    }

    return render(
        request,
        "proyectos/actividad_form.html",
        context,
    )

def actividad_editar(request, pk):
    actividad = get_object_or_404(
        ActividadProyecto.objects.select_related("proyecto"),
        pk=pk,
    )

    if request.method == "POST":
        form = ActividadProyectoForm(
            request.POST,
            instance=actividad,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Actividad actualizada correctamente.",
            )

            return redirect(
                "proyectos:proyecto_detalle",
                pk=actividad.proyecto.pk,
            )
    else:
        form = ActividadProyectoForm(
            instance=actividad,
        )

    context = {
        "form": form,
        "proyecto": actividad.proyecto,
        "actividad": actividad,
        "titulo": "Editar actividad",
        "boton": "Guardar cambios",
    }

    return render(
        request,
        "proyectos/actividad_form.html",
        context,
    )

def actividad_eliminar(request, pk):
    actividad = get_object_or_404(
        ActividadProyecto.objects.select_related("proyecto"),
        pk=pk,
    )

    proyecto_pk = actividad.proyecto.pk

    if request.method == "POST":
        actividad.delete()

        messages.success(
            request,
            "Actividad eliminada correctamente.",
        )

    return redirect(
        "proyectos:proyecto_detalle",
        pk=proyecto_pk,
    )


def cotizaciones_por_empresa(request):
    empresa_id = request.GET.get("empresa_id")

    if not empresa_id:
        return JsonResponse({"cotizaciones": []})

    cotizaciones = (
        Cotizacion.objects
        .filter(oportunidad__empresa_id=empresa_id)
        .select_related("oportunidad", "oportunidad__empresa")
        .order_by("-fecha_emision", "-pk")
    )

    resultados = []

    for cotizacion in cotizaciones:
        resultados.append(
            {
                "id": cotizacion.pk,
                "texto": (
                    f"{cotizacion.numero} - "
                    f"{cotizacion.oportunidad.titulo}"
                ),
            }
        )

    return JsonResponse({"cotizaciones": resultados})
    empresa_id = request.GET.get("empresa_id")

    if not empresa_id:
        return JsonResponse(
            {
                "cotizaciones": [],
            }
        )

    cotizaciones = (
        Cotizacion.objects.filter(
            oportunidad__empresa_id=empresa_id
        )
        .select_related(
            "oportunidad",
        )
        .order_by("-fecha_emision")
    )

    resultados = [
        {
            "id": cotizacion.pk,
            "texto": (
                f"{cotizacion.numero} - "
                f"{cotizacion.oportunidad.titulo}"
            ),
        }
        for cotizacion in cotizaciones
    ]

    return JsonResponse(
        {
            "cotizaciones": resultados,
        }
    )