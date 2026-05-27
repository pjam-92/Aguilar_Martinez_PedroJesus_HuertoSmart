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

"""¡! Explicación (imports): Se importa el módulo forms de Django y los tres
modelos cuyos datos necesitan formularios. Cultivo se importa solo para acceder
a sus CHOICES (DIFICULTAD_CHOICES, EXPOSICION_CHOICES, RIEGO_CHOICES) y
rellenar las opciones de los desplegables del filtro."""


# ESTILOS CSS COMPARTIDOS
# Clases de Tailwind CSS reutilizadas en todos los widgets para mantener coherencia visual

CSS_INPUT = 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-verde-medio'
CSS_SELECT = 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-verde-medio bg-white'

"""¡! Explicación (CSS_INPUT y CSS_SELECT): En lugar de repetir las clases de
Tailwind en cada campo, las definimos una vez como constantes y las reutilizamos.
Esto facilita cambiar el estilo de todos los formularios desde un solo punto."""

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

    """¡! Explicación (forms.Form vs ModelForm): Este formulario hereda de
    forms.Form porque su función es filtrar resultados, no crear ni editar
    registros en la base de datos. Los datos se envían por GET (en la URL)
    en lugar de por POST, porque queremos que la URL sea compartible con
    los filtros aplicados."""

    busqueda = forms.CharField(
        required=False, label='Buscar',
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre o nombre científico...',
            'class': CSS_INPUT,
        })
    )

    """¡! Explicación (required=False): Todos los campos del filtro son opcionales.
    Si el usuario no rellena un campo, ese filtro simplemente no se aplica.
    Por eso todos tienen required=False."""

    dificultad = forms.ChoiceField(
        required=False, label='Dificultad',
        choices=[('', 'Todas')] + Cultivo.DIFICULTAD_CHOICES,
        widget=forms.Select(attrs={'class': CSS_SELECT})
    )

    """¡! Explicación (choices en ChoiceField): Las opciones del desplegable se
    construyen añadiendo ('', 'Todas') al inicio de la lista DIFICULTAD_CHOICES
    del modelo. La opción vacía '' significa "sin filtro aplicado"."""

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

    """¡! Explicación (widget): El widget define qué elemento HTML se genera
    para cada campo. TextInput genera un <input type="text">, Select genera
    un <select>. Con attrs podemos añadir atributos HTML como class, placeholder
    o maxlength directamente desde Python."""


# FORMULARIO DE CREACIÓN DE HUERTO

class HuertoForm(forms.ModelForm):
    """Formulario para crear o editar un huerto."""

    """¡! Explicación (ModelForm): Al heredar de ModelForm y definir el modelo
    en la clase Meta, Django genera automáticamente los campos del formulario
    a partir de los campos del modelo Huerto. Solo hay que indicar qué campos
    incluir (fields) y personalizar sus widgets y etiquetas si se desea."""

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

    """¡! Explicación (campos excluidos): El campo usuario no aparece en el
    formulario porque se asigna automáticamente en la vista (huerto.usuario =
    request.user). El slug tampoco aparece porque se genera en el método save()
    del modelo. Nunca deben rellenarse por el usuario."""


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

    """¡! Explicación (DateInput con type date): Al especificar 'type': 'date'
    en el widget, el navegador muestra un selector de fecha visual en lugar de
    un campo de texto normal. Es una mejora de usabilidad que no requiere
    ninguna librería externa, solo HTML5."""
