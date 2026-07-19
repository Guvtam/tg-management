import os
from django import forms

from .models import Proyecto, ActividadProyecto, DocumentoProyecto
from cotizaciones.models import Cotizacion




class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto

        fields = [
            "nombre",
            "empresa",
            "cotizacion",
            "responsable",
            "fecha_alta",
            "fecha_entrega",
            "estado",
            "prioridad",
            
            "descripcion",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del proyecto",
                }
            ),
            "empresa": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "cotizacion": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "responsable": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "fecha_alta": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
            ),
            "fecha_entrega": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
            ),
            "estado": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "prioridad": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
           
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Descripción general del proyecto",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["fecha_alta"].input_formats = ["%Y-%m-%d"]
        self.fields["fecha_entrega"].input_formats = ["%Y-%m-%d"]

        empresa_id = None

        # Cuando el formulario se envía
        if self.is_bound:
            empresa_id = self.data.get("empresa")

        # Cuando se está editando
        elif self.instance and self.instance.pk:
            empresa_id = self.instance.empresa_id

        if empresa_id:
            try:
                empresa_id = int(empresa_id)

                self.fields["cotizacion"].queryset = (
                    Cotizacion.objects
                    .filter(
                        oportunidad__empresa_id=empresa_id
                    )
                    .select_related(
                        "oportunidad",
                        "oportunidad__empresa",
                    )
                    .order_by("-pk")
                )

            except (TypeError, ValueError):
                self.fields["cotizacion"].queryset = (
                    Cotizacion.objects.none()
                )
        else:
            self.fields["cotizacion"].queryset = (
                Cotizacion.objects.none()
            )

    def clean(self):
        cleaned_data = super().clean()

        empresa = cleaned_data.get("empresa")
        cotizacion = cleaned_data.get("cotizacion")

        if empresa and cotizacion:
            if cotizacion.oportunidad.empresa_id != empresa.pk:
                self.add_error(
                    "cotizacion",
                    "La cotización no pertenece al cliente seleccionado.",
                )

        return cleaned_data
    

class ActividadProyectoForm(forms.ModelForm):
    class Meta:
        model = ActividadProyecto

        fields = [
            "titulo",
            "tipo",
            "responsable",
            "estado",
            "fecha",
            "descripcion",
        ]

        widgets = {
            "titulo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre de la actividad",
                }
            ),
            "tipo": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "responsable": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "estado": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "fecha": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Detalle u observaciones",
                }
            ),
        }


class DocumentoProyectoForm(forms.ModelForm):
    class Meta:
        model = DocumentoProyecto

        fields = [
            "nombre",
            "tipo",
            "descripcion",
            "archivo",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: Minuta reunión inicial",
                }
            ),
            "tipo": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Descripción, versión, propósito "
                        "u observaciones del documento"
                    ),
                }
            ),
            "archivo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": (
                        ".pdf,.doc,.docx,.xls,.xlsx,"
                        ".ppt,.pptx,.txt,.csv,"
                        ".jpg,.jpeg,.png,.webp,.zip"
                    ),
                }
            ),
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get("archivo")

        # Cuando se edita un documento sin reemplazar el archivo,
        # Django puede conservar el archivo actual.
        if not archivo:
            return archivo

        extensiones_permitidas = {
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".txt",
            ".csv",
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".zip",
        }

        

        extension = os.path.splitext(archivo.name)[1].lower()

        if extension not in extensiones_permitidas:
            raise forms.ValidationError(
                "El tipo de archivo no está permitido. "
                "Puede cargar PDF, Word, Excel, PowerPoint, "
                "imágenes, texto, CSV o ZIP."
            )

        limite_mb = 20
        limite_bytes = limite_mb * 1024 * 1024

        if archivo.size > limite_bytes:
            raise forms.ValidationError(
                f"El archivo no puede superar los {limite_mb} MB."
            )

        return archivo