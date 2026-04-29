from django import forms
from django.core import validators
from django.core.exceptions import ValidationError


class Formgestor(forms.Form):
    # usuario_id=forms.IntegerField(label="Ingrese el ID del usuario del gestor")
    departamento = forms.CharField(
        max_length=50,
        label="Ingrese el departamento del gestor",
        min_length=1,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Departamento del gestor'}),
        validators=[
            validators.RegexValidator(
                regex='^[a-zA-Z\s]+$',
                message='El departamento solo puede contener letras y espacios',
                code='invalid_departamento'
            ),
            validators.MinLengthValidator(
                limit_value=2,
                message='El departamento debe tener al menos 2 caracteres.'
            )
        ]
    )

    telefono = forms.CharField(max_length=20, label="Ingrese el teléfono del gestor")
    telefono.widget.attrs.update({'placeholder': 'Teléfono del gestor'})

    # activo=forms.BooleanField(required=False, label="¿El gestor está activo?")
    opcionesactivo = []