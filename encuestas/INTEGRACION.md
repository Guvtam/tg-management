# Módulo Encuestas para TG Management

Adaptado al repositorio `Guvtam/tg-management` revisado el 19-07-2026.

## 1. Copiar la aplicación

Copia la carpeta `encuestas` en la raíz del proyecto, al mismo nivel que `crm`, `proyectos` y `cotizaciones`.

## 2. Registrar la aplicación

En `config/settings.py`, agrega `encuestas` dentro de `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "proyectos",
    "encuestas",
    "finanzas",
    # ...
]
```

## 3. Registrar las URL

En `config/urls.py`, agrega:

```python
path("encuestas/", include("encuestas.urls")),
```

## 4. Agregar al menú lateral

En `core/templates/core/base.html`, agrega dentro de `<ul class="menu">`:

```html
<li><a href="{% url 'encuestas:lista' %}">Satisfacción de clientes</a></li>
```

## 5. Integrar con el detalle de proyecto

En `proyectos/templates/proyectos/proyecto_detalle.html`, agrega donde quieras mostrar la encuesta:

```html
<div class="panel">
    <h2>Encuesta de satisfacción</h2>
    {% if proyecto.encuesta_satisfaccion %}
        <p>
            Estado:
            <span class="estado estado-{{ proyecto.encuesta_satisfaccion.estado }}">
                {{ proyecto.encuesta_satisfaccion.get_estado_display }}
            </span>
        </p>
        <a class="boton" href="{% url 'encuestas:detalle' proyecto.encuesta_satisfaccion.pk %}">
            Ver encuesta
        </a>
    {% else %}
        <p class="texto-secundario">Este proyecto aún no tiene encuesta.</p>
        <a class="boton" href="{% url 'encuestas:crear_desde_proyecto' proyecto.pk %}">
            Crear encuesta
        </a>
    {% endif %}
</div>
```

Django permite consultar una relación `OneToOneField` en una plantilla. Cuando no existe, la condición se evalúa como falsa.

## 6. Crear la tabla

Desde Git Bash, en la carpeta del proyecto:

```bash
python manage.py migrate
python manage.py check
python manage.py test encuestas
python manage.py runserver
```

La migración incluida depende de:

- `crm.0002_alter_actividad_options`
- `proyectos.0006_documentoproyecto`

Estas son las migraciones vigentes observadas en tu repositorio.

## Funciones incluidas

- Encuesta única por proyecto.
- Cliente sincronizado automáticamente desde el proyecto.
- Contactos filtrados por empresa al crear desde un proyecto.
- Enlace público UUID no predecible.
- Respuesta sin inicio de sesión.
- Bloqueo de segunda respuesta.
- Fecha de vencimiento opcional.
- Estados pendiente, enviada, respondida, vencida y anulada.
- Preguntas de satisfacción 1–5.
- Recomendación 0–10 y categoría NPS.
- Comentarios, oportunidades de mejora y testimonio autorizado.
- Lista interna con filtros e indicadores.
- Administración Django.
- Pruebas automatizadas.

## Nota para producción

El enlace público se construye con el dominio desde el que accedas al sistema. Antes de enviarlo a clientes, configura `ALLOWED_HOSTS`, HTTPS y un dominio real. No uses el servidor de desarrollo de Django para producción.
