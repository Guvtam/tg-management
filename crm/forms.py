from django import forms

from .models import Empresa, Contacto, Oportunidad, Actividad


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa

        fields = [
            "razon_social",
            "nombre_fantasia",
            "rut",
            "tipo",
            "rubro",
            "sitio_web",
            "telefono",
            "email",
            "direccion",
            "comuna",
            "region",
            "estado",
            "observaciones",
        ]

        widgets = {
            "razon_social": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: Empresa Ejemplo SpA",
                }
            ),
            "nombre_fantasia": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: Empresa Ejemplo",
                }
            ),
            "rut": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: 76.123.456-7",
                }
            ),
            "tipo": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "rubro": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: Construcción",
                }
            ),
            "sitio_web": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://...",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+56 9 ...",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "contacto@empresa.cl",
                }
            ),
            "direccion": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "comuna": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "region": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: Valparaíso",
                }
            ),
            "estado": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Información adicional de la empresa...",
                }
            ),
        }


class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto

        fields = [
            "empresa",
            "nombres",
            "apellidos",
            "cargo",
            "email",
            "telefono",
            "es_contacto_principal",
            "activo",
            "observaciones",
        ]

        widgets = {
            "empresa": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "nombres": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: Andrea",
                }
            ),
            "apellidos": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: Pérez González",
                }
            ),
            "cargo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: Gerente de Operaciones",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "contacto@empresa.cl",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+56 9 1234 5678",
                }
            ),
            "es_contacto_principal": forms.CheckboxInput(
                attrs={
                    "class": "form-check",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Información adicional del contacto...",
                }
            ),
        }       

class OportunidadForm(forms.ModelForm):
    class Meta:
        model = Oportunidad

        fields = [
            "titulo",
            "empresa",
            "contacto",
            "descripcion",
            "servicio_interes",
            "etapa",
            "prioridad",
            "valor_estimado",
            "probabilidad",
            "fecha_estimada_cierre",
            "responsable",
            "motivo_perdida",
        ]

        widgets = {
            "titulo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: Desarrollo de sitio web corporativo",
                }
            ),
            "empresa": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "contacto": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe la necesidad o alcance preliminar...",
                }
            ),
            "servicio_interes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: Desarrollo web, Power BI, automatización",
                }
            ),
            "etapa": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "prioridad": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "valor_estimado": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "1",
                    "placeholder": "Ej.: 850000",
                }
            ),
            "probabilidad": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "100",
                    "step": "1",
                }
            ),
            "fecha_estimada_cierre": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "responsable": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "motivo_perdida": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Completar cuando la oportunidad sea perdida.",
                }
            ),
        }

    def clean_probabilidad(self):
        probabilidad = self.cleaned_data.get("probabilidad")

        if probabilidad is not None and not 0 <= probabilidad <= 100:
            raise forms.ValidationError(
                "La probabilidad debe estar entre 0 y 100."
            )

        return probabilidad

    def clean(self):
        cleaned_data = super().clean()

        etapa = cleaned_data.get("etapa")
        motivo_perdida = cleaned_data.get("motivo_perdida")

        if (
            etapa == Oportunidad.Etapa.PERDIDA
            and not motivo_perdida
        ):
            self.add_error(
                "motivo_perdida",
                "Debes indicar el motivo cuando la oportunidad está perdida.",
            )

        return cleaned_data
    
class ActividadForm(forms.ModelForm):
    fecha_programada = forms.DateTimeField(
        label="Fecha programada",
        required=True,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "class": "form-control",
                "type": "datetime-local",
            },
        ),
    )

    class Meta:
        model = Actividad

        fields = [
            "oportunidad",
            "tipo",
            "asunto",
            "descripcion",
            "fecha_programada",
            "estado",
            "responsable",
            "resultado",
        ]
        

        widgets = {
            "oportunidad": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "tipo": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "asunto": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: Reunión de levantamiento",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe lo que se debe realizar...",
                }
            ),
            "estado": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "responsable": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "resultado": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Resultado o conclusión de la actividad...",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        estado = cleaned_data.get("estado")
        resultado = cleaned_data.get("resultado")

        if (
            estado == Actividad.EstadoActividad.COMPLETADA
            and not resultado
        ):
            self.add_error(
                "resultado",
                "Debes indicar un resultado cuando la actividad está completada.",
            )

        return cleaned_data