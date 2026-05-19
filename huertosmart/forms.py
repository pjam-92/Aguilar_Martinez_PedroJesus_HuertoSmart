# forms.py — Formularios de HuertoSmart
"""
Este archivo define los formularios Django del proyecto. Un formulario en Django
es una clase Python que se encarga de tres cosas:
1. Generar el HTML del formulario automáticamente.
2. Validar los datos que envía el usuario.
3. Limpiar y preparar los datos para guardarlos en la base de datos.

Hay dos tipos de formularios en Django:
- forms.Form: formulario genérico, no vinculado a ningún modelo.
- forms.ModelForm: formulario vinculado a un modelo, genera los campos
  automáticamente a partir de los campos del modelo.

En este proyecto se usan ambos tipos.
"""

from django import forms
from .models import Cultivo, Huerto, Siembra



# ESTILOS CSS COMPARTIDOS
# Clases de Tailwind CSS reutilizadas en todos los widgets para mantener coherencia visual

CSS_INPUT = 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-verde-medio'
CSS_SELECT = 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-verde-medio bg-white'


# Lista de meses del año para el filtro de mes de siembra
MESES_CHOICES = [
    ('', 'Cualquier mes'),
    ('enero', 'Enero'), ('febrero', 'Febrero'), ('marzo', 'Marzo'),
    ('abril', 'Abril'), ('mayo', 'Mayo'), ('junio', 'Junio'),
    ('julio', 'Julio'), ('agosto', 'Agosto'), ('septiembre', 'Septiembre'),
    ('octubre', 'Octubre'), ('noviembre', 'Noviembre'), ('diciembre', 'Diciembre'),
]


# FORMULARIO DE FILTRO DE CULTIVOS
# Hereda de forms.Form (no de ModelForm) porque no guarda datos en la base de datos

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



# FORMULARIO DE CREACIÓN DE HUERTO

class HuertoForm(forms.ModelForm):
    """Formulario para crear o editar un huerto."""


    class Meta:
        model = Huerto
        # Solo mostramos estos campos — el usuario y el slug los gestiona el sistema
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



# FORMULARIO DE NUEVA SIEMBRA

class SiembraForm(forms.ModelForm):
    """Formulario para registrar una nueva siembra en un huerto."""

    class Meta:
        model = Siembra
        # El campo huerto no se incluye — se asigna automáticamente en la vista
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

