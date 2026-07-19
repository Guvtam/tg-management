from django import forms

from cotizaciones.models import Cotizacion
from proyectos.models import Proyecto

from .models import Gasto, Ingreso


class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso

        fields = [
            "empresa",
            "proyecto",
            "cotizacion",
            "concepto",
            "monto",
            "moneda",
            "fecha_emision",
            "fecha_vencimiento",
            "fecha_pago",
            "estado",
            "observaciones",
        ]

        widgets = {
            "empresa": forms.Select(
                attrs={"class": "form-control"}
            ),
            "proyecto": forms.Select(
                attrs={"class": "form-control"}
            ),
            "cotizacion": forms.Select(
                attrs={"class": "form-control"}
            ),
            "concepto": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ejemplo: Anticipo desarrollo web",
                }
            ),
            "monto": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0.01",
                    "step": "0.01",
                }
            ),
            "moneda": forms.Select(
                attrs={"class": "form-control"}
            ),
            "fecha_emision": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
            ),
            "fecha_vencimiento": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
            ),
            "fecha_pago": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
            ),
            "estado": forms.Select(
                attrs={"class": "form-control"}
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Observaciones del ingreso",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        empresa_id = None

        if self.is_bound:
            empresa_id = self.data.get("empresa")

        elif self.instance and self.instance.pk:
            empresa_id = self.instance.empresa_id

        self.fields["proyecto"].queryset = (
            Proyecto.objects.none()
        )

        self.fields["cotizacion"].queryset = (
            Cotizacion.objects.none()
        )

        if empresa_id:
            try:
                empresa_id = int(empresa_id)

                self.fields["proyecto"].queryset = (
                    Proyecto.objects
                    .filter(empresa_id=empresa_id)
                    .order_by("-creado_en")
                )

                self.fields["cotizacion"].queryset = (
                    Cotizacion.objects
                    .filter(
                        oportunidad__empresa_id=empresa_id
                    )
                    .select_related("oportunidad")
                    .order_by("-fecha_emision", "-pk")
                )

            except (TypeError, ValueError):
                pass

    def clean(self):
        cleaned_data = super().clean()

        empresa = cleaned_data.get("empresa")
        proyecto = cleaned_data.get("proyecto")
        cotizacion = cleaned_data.get("cotizacion")
        fecha_emision = cleaned_data.get("fecha_emision")
        fecha_vencimiento = cleaned_data.get(
            "fecha_vencimiento"
        )
        fecha_pago = cleaned_data.get("fecha_pago")
        estado = cleaned_data.get("estado")

        if empresa and proyecto:
            if proyecto.empresa_id != empresa.pk:
                self.add_error(
                    "proyecto",
                    "El proyecto seleccionado no pertenece al cliente.",
                )

        if empresa and cotizacion:
            if cotizacion.oportunidad.empresa_id != empresa.pk:
                self.add_error(
                    "cotizacion",
                    "La cotización seleccionada no pertenece al cliente.",
                )

        if (
            fecha_emision
            and fecha_vencimiento
            and fecha_vencimiento < fecha_emision
        ):
            self.add_error(
                "fecha_vencimiento",
                "La fecha de vencimiento no puede ser anterior a la emisión.",
            )

        if (
            fecha_emision
            and fecha_pago
            and fecha_pago < fecha_emision
        ):
            self.add_error(
                "fecha_pago",
                "La fecha de pago no puede ser anterior a la emisión.",
            )

        if estado == Ingreso.Estado.PAGADO and not fecha_pago:
            self.add_error(
                "fecha_pago",
                "Debes ingresar la fecha de pago.",
            )

        return cleaned_data


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto

        fields = [
            "proyecto",
            "categoria",
            "proveedor",
            "concepto",
            "monto",
            "moneda",
            "fecha",
            "observaciones",
        ]

        widgets = {
            "proyecto": forms.Select(
                attrs={"class": "form-control"}
            ),
            "categoria": forms.Select(
                attrs={"class": "form-control"}
            ),
            "proveedor": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del proveedor",
                }
            ),
            "concepto": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ejemplo: Hosting anual",
                }
            ),
            "monto": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0.01",
                    "step": "0.01",
                }
            ),
            "moneda": forms.Select(
                attrs={"class": "form-control"}
            ),
            "fecha": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Observaciones del gasto",
                }
            ),
        }