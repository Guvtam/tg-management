from django import forms

from .models import ModalidadPagoCotizacion


class ModalidadPagoCotizacionForm(forms.ModelForm):
    class Meta:
        model = ModalidadPagoCotizacion
        fields = [
            "mostrar_pago_unico",
            "descuento_pago_unico",
            "mostrar_plan_12_meses",
            "porcentaje_pie",
            "mantencion_mensual",
            "observaciones",
        ]
        widgets = {
            "mostrar_pago_unico": forms.CheckboxInput(
                attrs={"class": "mp-switch-input", "data-toggle-target": "pago-unico"}
            ),
            "descuento_pago_unico": forms.NumberInput(
                attrs={
                    "class": "mp-input",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                    "inputmode": "decimal",
                    "placeholder": "Ej.: 5",
                    "data-calculo": "descuento",
                }
            ),
            "mostrar_plan_12_meses": forms.CheckboxInput(
                attrs={"class": "mp-switch-input", "data-toggle-target": "plan-12"}
            ),
            "porcentaje_pie": forms.NumberInput(
                attrs={
                    "class": "mp-input",
                    "step": "0.01",
                    "min": "0.01",
                    "max": "99.99",
                    "inputmode": "decimal",
                    "placeholder": "Ej.: 40",
                    "data-calculo": "pie",
                }
            ),
            "mantencion_mensual": forms.NumberInput(
                attrs={
                    "class": "mp-input",
                    "step": "1",
                    "min": "0",
                    "inputmode": "decimal",
                    "placeholder": "Ej.: 45000",
                    "data-calculo": "mantencion",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "mp-textarea",
                    "rows": 4,
                    "placeholder": (
                        "Ej.: La mantención incluye hosting, respaldos, soporte y "
                        "actualizaciones menores."
                    ),
                }
            ),
        }
        labels = {
            "descuento_pago_unico": "Descuento por pago contado",
            "porcentaje_pie": "Porcentaje de pie inicial",
            "mantencion_mensual": "Mantención y soporte mensual",
        }

    def clean(self):
        datos = super().clean()
        if not datos.get("mostrar_pago_unico") and not datos.get("mostrar_plan_12_meses"):
            raise forms.ValidationError("Debes habilitar al menos una modalidad de pago.")
        return datos
