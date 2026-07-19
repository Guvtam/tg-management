from django import forms

from .models import InteraccionTicket, Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "empresa",
            "contacto",
            "proyecto",
            "titulo",
            "descripcion",
            "categoria",
            "prioridad",
            "canal",
            "responsable",
        ]
        widgets = {
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
            "proyecto": forms.Select(
                attrs={
                    
                    "class": "form-control",
                    }
                    ),
            "titulo": forms.TextInput(
                attrs={
                    
                    "class": "form-control",
                    }
                    ),
            "descripcion": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    }
                    ),
            "categoria": forms.Select(
                attrs={
                    
                    "class": "form-control",
                    }
                    ),
            "prioridad": forms.Select(
                attrs={
                    
                    "class": "form-control",
                    }
                    ),
            "canal": forms.Select(
                attrs={
                    
                    "class": "form-control",
                    }
                    ),
            "responsable": forms.Select(
                attrs={
                    
                    "class": "form-control",
                    }
                    ),
            
        }


class TicketEstadoForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "estado",
            "horas_dedicadas",
        ]
        widgets = {
            "estado": forms.Select(
                attrs={
                    "class": "form-control",
                    }
                    ),
            "horas_dedicadas": forms.TextInput(
                attrs={
                    "class": "form-control",
                    }
                    ),
        }

class InteraccionTicketForm(forms.ModelForm):
    class Meta:
        model = InteraccionTicket
        fields = [
            "tipo",
            "mensaje",
        ]
        widgets = {
            "tipo": forms.Select(
                attrs={
                   
                    "class": "form-control",
                    }
                    ),
            "mensaje": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                    }
                    ),
        }
