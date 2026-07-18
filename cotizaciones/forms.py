from django import forms

from .models import Cotizacion, ItemCotizacion


class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion

        exclude = (
            "numero",
            "creado_por",
            "fecha_creacion",
            "fecha_actualizacion",
        )

        widgets = {
            "oportunidad": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "contacto": forms.Select(
                attrs={
                    "class": "form-control",
                }
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
            "estado": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "moneda": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "valor_moneda": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.0001",
                    "min": "0.0001",
                    "placeholder": "Ej.: 1 para CLP",
                }
            ),
            "descuento_porcentaje": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "impuesto_porcentaje": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "condiciones_pago": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: 30 días contra factura",
                }
            ),
            "plazo_entrega": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: 20 días hábiles",
                }
            ),
            "validez_oferta": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej.: 15 días",
                }
            ),
            "alcance": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Describe los productos, servicios y trabajos "
                        "incluidos en la cotización."
                    ),
                }
            ),
            "exclusiones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Indica los trabajos, materiales o servicios "
                        "que no están incluidos."
                    ),
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Agrega observaciones comerciales o técnicas."
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["oportunidad"].empty_label = (
            "Seleccione una oportunidad"
        )

        self.fields["contacto"].empty_label = (
            "Seleccione un contacto"
        )

        self.fields["fecha_emision"].input_formats = [
            "%Y-%m-%d",
        ]

        self.fields["fecha_vencimiento"].input_formats = [
            "%Y-%m-%d",
        ]

        self.fields["contacto"].required = False
        self.fields["fecha_vencimiento"].required = False

    def clean(self):
        cleaned_data = super().clean()

        oportunidad = cleaned_data.get("oportunidad")
        contacto = cleaned_data.get("contacto")
        fecha_emision = cleaned_data.get("fecha_emision")
        fecha_vencimiento = cleaned_data.get(
            "fecha_vencimiento"
        )
        moneda = cleaned_data.get("moneda")
        valor_moneda = cleaned_data.get("valor_moneda")
        descuento_porcentaje = cleaned_data.get(
            "descuento_porcentaje"
        )
        impuesto_porcentaje = cleaned_data.get(
            "impuesto_porcentaje"
        )

        if (
            fecha_emision
            and fecha_vencimiento
            and fecha_vencimiento < fecha_emision
        ):
            self.add_error(
                "fecha_vencimiento",
                (
                    "La fecha de vencimiento no puede ser "
                    "anterior a la fecha de emisión."
                ),
            )

        if moneda == Cotizacion.Moneda.CLP:
            if valor_moneda != 1:
                self.add_error(
                    "valor_moneda",
                    (
                        "Para cotizaciones en CLP, el valor de "
                        "la moneda debe ser 1."
                    ),
                )

        if moneda in {
            Cotizacion.Moneda.UF,
            Cotizacion.Moneda.USD,
        }:
            if valor_moneda is not None and valor_moneda <= 1:
                self.add_error(
                    "valor_moneda",
                    (
                        "Para UF o USD debes ingresar su valor "
                        "actual expresado en pesos chilenos."
                    ),
                )

        if (
            descuento_porcentaje is not None
            and not 0 <= descuento_porcentaje <= 100
        ):
            self.add_error(
                "descuento_porcentaje",
                (
                    "El descuento general debe estar entre "
                    "0 y 100."
                ),
            )

        if (
            impuesto_porcentaje is not None
            and not 0 <= impuesto_porcentaje <= 100
        ):
            self.add_error(
                "impuesto_porcentaje",
                (
                    "El impuesto debe estar entre 0 y 100."
                ),
            )

        if oportunidad and contacto:
            if contacto.empresa_id != oportunidad.empresa_id:
                self.add_error(
                    "contacto",
                    (
                        "El contacto seleccionado no pertenece "
                        "a la empresa de la oportunidad."
                    ),
                )

        return cleaned_data


class ItemCotizacionForm(forms.ModelForm):
    class Meta:
        model = ItemCotizacion

        exclude = (
            "cotizacion",
        )

        widgets = {
            "orden": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            
            "descripcion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Ej.: Desarrollo de sitio web corporativo"
                    ),
                }
            ),
            "codigo": forms.TextInput(
                attrs={
                    "readonly": "readonly",
                }
            ),
            "detalle": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Describe el alcance específico de este ítem."
                    ),
                }
            ),
            "cantidad": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "unidad": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Ej.: Unidad, Hora, Mes o Servicio"
                    ),
                }
            ),
            "precio_unitario": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "descuento_porcentaje": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["codigo"].required = False
        self.fields["detalle"].required = False

    def clean(self):
        cleaned_data = super().clean()

        orden = cleaned_data.get("orden")
        descripcion = cleaned_data.get("descripcion")
        cantidad = cleaned_data.get("cantidad")
        unidad = cleaned_data.get("unidad")
        precio_unitario = cleaned_data.get(
            "precio_unitario"
        )
        descuento_porcentaje = cleaned_data.get(
            "descuento_porcentaje"
        )

        if orden is not None and orden < 1:
            self.add_error(
                "orden",
                "El orden debe ser igual o mayor que 1.",
            )

        if descripcion:
            cleaned_data["descripcion"] = (
                descripcion.strip()
            )

        if not descripcion or not descripcion.strip():
            self.add_error(
                "descripcion",
                "Debes ingresar una descripción.",
            )

        if cantidad is not None and cantidad <= 0:
            self.add_error(
                "cantidad",
                "La cantidad debe ser mayor que cero.",
            )

        if unidad:
            cleaned_data["unidad"] = unidad.strip()

        if not unidad or not unidad.strip():
            self.add_error(
                "unidad",
                "Debes indicar una unidad.",
            )

        if (
            precio_unitario is not None
            and precio_unitario < 0
        ):
            self.add_error(
                "precio_unitario",
                "El precio unitario no puede ser negativo.",
            )

        if (
            descuento_porcentaje is not None
            and not 0 <= descuento_porcentaje <= 100
        ):
            self.add_error(
                "descuento_porcentaje",
                (
                    "El descuento debe estar entre "
                    "0 y 100."
                ),
            )

        return cleaned_data