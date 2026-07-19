from django import forms

from crm.models import Contacto
from proyectos.models import Proyecto

from .models import EncuestaSatisfaccion


class EncuestaCrearForm(forms.ModelForm):
    class Meta:
        model = EncuestaSatisfaccion
        fields = ["proyecto", "contacto", "fecha_vencimiento"]
        widgets = {
            "proyecto": forms.Select(attrs={"class": "form-control"}),
            "contacto": forms.Select(attrs={"class": "form-control"}),
            "fecha_vencimiento": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["proyecto"].queryset = Proyecto.objects.select_related(
            "empresa"
        ).order_by("-creado_en")
        self.fields["contacto"].queryset = Contacto.objects.filter(
            activo=True
        ).select_related("empresa")

        if proyecto is not None:
            self.fields["proyecto"].initial = proyecto
            self.fields["proyecto"].widget = forms.HiddenInput()
            self.fields["contacto"].queryset = Contacto.objects.filter(
                empresa=proyecto.empresa,
                activo=True,
            )

    def clean(self):
        cleaned_data = super().clean()
        proyecto = cleaned_data.get("proyecto")
        contacto = cleaned_data.get("contacto")
        if proyecto and contacto and contacto.empresa_id != proyecto.empresa_id:
            self.add_error(
                "contacto",
                "El contacto seleccionado no pertenece al cliente del proyecto.",
            )
        return cleaned_data


class EncuestaRespuestaForm(forms.ModelForm):
    ESCALA_5 = [(numero, str(numero)) for numero in range(1, 6)]
    ESCALA_10 = [(numero, str(numero)) for numero in range(0, 11)]

    satisfaccion_general = forms.TypedChoiceField(
        label="¿Qué tan satisfecho(a) estás con el servicio recibido?",
        choices=ESCALA_5,
        coerce=int,
        widget=forms.RadioSelect,
    )
    calidad_solucion = forms.TypedChoiceField(
        label="¿Cómo evaluarías la calidad de la solución entregada?",
        choices=ESCALA_5,
        coerce=int,
        widget=forms.RadioSelect,
    )
    comunicacion = forms.TypedChoiceField(
        label="¿Cómo evaluarías la comunicación durante el proyecto?",
        choices=ESCALA_5,
        coerce=int,
        widget=forms.RadioSelect,
    )
    cumplimiento_plazos = forms.TypedChoiceField(
        label="¿Cómo evaluarías el cumplimiento de los plazos acordados?",
        choices=ESCALA_5,
        coerce=int,
        widget=forms.RadioSelect,
    )
    recomendacion = forms.TypedChoiceField(
        label="¿Qué tan probable es que recomiendes nuestros servicios?",
        choices=ESCALA_10,
        coerce=int,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = EncuestaSatisfaccion
        fields = [
            "satisfaccion_general",
            "calidad_solucion",
            "cumplimiento_expectativas",
            "comunicacion",
            "cumplimiento_plazos",
            "recomendacion",
            "aspectos_valorados",
            "aspectos_mejora",
            "testimonio",
            "autoriza_testimonio",
        ]
        widgets = {
            "cumplimiento_expectativas": forms.RadioSelect,
            "aspectos_valorados": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "aspectos_mejora": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "testimonio": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "autoriza_testimonio": forms.CheckboxInput(
                attrs={"class": "form-check"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("autoriza_testimonio") and not cleaned_data.get(
            "testimonio", ""
        ).strip():
            self.add_error(
                "testimonio",
                "Escribe un testimonio antes de autorizar su publicación.",
            )
        return cleaned_data
