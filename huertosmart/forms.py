"""
Formularios de Django para HuertoSmart.
"""
from django import forms
from .models import Cultivo, Huerto, Siembra


# FILTRO DE CULTIVOS

MESES_CHOICES = [
    ('', 'Cualquier mes'),
    ('enero', 'Enero'), ('febrero', 'Febrero'), ('marzo', 'Marzo'),
    ('abril', 'Abril'), ('mayo', 'Mayo'), ('junio', 'Junio'),
    ('julio', 'Julio'), ('agosto', 'Agosto'), ('septiembre', 'Septiembre'),
    ('octubre', 'Octubre'), ('noviembre', 'Noviembre'), ('diciembre', 'Diciembre'),
]

CSS_INPUT = 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-verde-medio'
CSS_SELECT = 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-verde-medio bg-white'


class CultivoFilterForm(forms.Form):
    """Formulario de filtros para la biblioteca de cultivos (método GET)."""

    busqueda = forms.CharField(
        required=False, label='Buscar',
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre o nombre científico...',
            'class': CSS_INPUT,
        })
    )
    dificultad = forms.ChoiceField(
        required=False, label='Dificultad',
        choices=[('', 'Todas')] + Cultivo.DIFICULTAD_CHOICES,
        widget=forms.Select(attrs={'class': CSS_SELECT})
    )
    exposicion = forms.ChoiceField(
        required=False, label='Exposición',
        choices=[('', 'Todas')] + Cultivo.EXPOSICION_CHOICES,
        widget=forms.Select(attrs={'class': CSS_SELECT})
    )
    riego = forms.ChoiceField(
        required=False, label='Riego',
        choices=[('', 'Todos')] + Cultivo.RIEGO_CHOICES,
        widget=forms.Select(attrs={'class': CSS_SELECT})
    )
    mes_siembra = forms.ChoiceField(
        required=False, label='Mes de siembra',
        choices=MESES_CHOICES,
        widget=forms.Select(attrs={'class': CSS_SELECT})
    )


# FORMULARIOS DEL HUERTO

class HuertoForm(forms.ModelForm):
    """Formulario para crear o editar un huerto."""

    class Meta:
        model = Huerto
        fields = ['nombre', 'ubicacion', 'municipio', 'codigo_postal', 'superficie_m2']
        labels = {
            'nombre': 'Nombre del huerto',
            'ubicacion': 'Tipo de ubicación',
            'municipio': 'Municipio',
            'codigo_postal': 'Código postal',
            'superficie_m2': 'Superficie (m²)',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Mi huerto de tomates, El rincón verde...',
                'class': CSS_INPUT,
            }),
            'ubicacion': forms.Select(attrs={'class': CSS_SELECT}),
            'municipio': forms.TextInput(attrs={
                'placeholder': 'Murcia, Cartagena...',
                'class': CSS_INPUT,
            }),
            'codigo_postal': forms.TextInput(attrs={
                'placeholder': '30001', 'maxlength': '5',
                'class': CSS_INPUT,
            }),
            'superficie_m2': forms.NumberInput(attrs={
                'placeholder': '10', 'min': '0', 'step': '0.5',
                'class': CSS_INPUT,
            }),
        }


class SiembraForm(forms.ModelForm):
    """Formulario para registrar una nueva siembra en un huerto."""

    class Meta:
        model = Siembra
        fields = ['cultivo', 'fecha_siembra', 'fecha_cosecha_estimada', 'cantidad', 'estado', 'notas']
        labels = {
            'cultivo': 'Cultivo',
            'fecha_siembra': 'Fecha de siembra',
            'fecha_cosecha_estimada': 'Cosecha estimada (opcional)',
            'cantidad': 'Número de plantas',
            'estado': 'Estado',
            'notas': 'Notas',
        }
        widgets = {
            'cultivo': forms.Select(attrs={'class': CSS_SELECT}),
            'fecha_siembra': forms.DateInput(attrs={'type': 'date', 'class': CSS_INPUT}),
            'fecha_cosecha_estimada': forms.DateInput(attrs={'type': 'date', 'class': CSS_INPUT}),
            'cantidad': forms.NumberInput(attrs={'min': '1', 'class': CSS_INPUT}),
            'estado': forms.Select(attrs={'class': CSS_SELECT}),
            'notas': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Observaciones, condiciones especiales...',
                'class': CSS_INPUT,
            }),
        }
