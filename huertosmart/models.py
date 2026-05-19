# models.py — Modelos de datos de HuertoSmart
"""
Este archivo define la estructura de la base de datos del proyecto.
Cada clase que hereda de models.Model es una tabla en la base de datos.
Cada atributo de la clase es una columna de esa tabla.

Django lee este archivo y genera automáticamente las tablas en SQLite
cuando ejecutamos 'python manage.py migrate'. Nunca hay que crear
las tablas a mano en SQL — Django lo hace todo por nosotros.

Modelos definidos en este archivo:
- Cultivo: catálogo de los 20 cultivos disponibles en la plataforma
- Enfermedad: catálogo de enfermedades que el modelo IA puede detectar
- Huerto: el huerto de un usuario
- Siembra: una siembra concreta dentro de un huerto
- Diagnostico: resultado de un análisis de IA sobre una foto
- Incidencia: notas e incidencias del usuario sobre sus siembras
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify



# MODELO CULTIVO
# Catálogo de cultivos disponibles. Los 20 registros se cargan con el fixture cultivos.json

class Cultivo(models.Model):
    """Biblioteca de cultivos disponibles en la plataforma."""


    # Opciones posibles para el campo dificultad
    DIFICULTAD_CHOICES = [
        ('facil', 'Fácil'),
        ('media', 'Media'),
        ('dificil', 'Difícil'),
    ]

    # Opciones posibles para el campo exposicion solar
    EXPOSICION_CHOICES = [
        ('sol', 'Sol pleno'),
        ('semisombra', 'Semisombra'),
        ('sombra', 'Sombra'),
    ]

    # Opciones posibles para el campo riego
    RIEGO_CHOICES = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
    ]

    # Campos del modelo — cada uno se convierte en una columna de la tabla
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)


    nombre_cientifico = models.CharField(max_length=150, blank=True)
    descripcion = models.TextField()
    dificultad = models.CharField(max_length=10, choices=DIFICULTAD_CHOICES)
    exposicion = models.CharField(max_length=15, choices=EXPOSICION_CHOICES)
    riego = models.CharField(max_length=10, choices=RIEGO_CHOICES)
    meses_siembra = models.CharField(max_length=50, help_text="Ej: 'marzo,abril,mayo'")
    meses_cosecha = models.CharField(max_length=50, help_text="Ej: 'julio,agosto,septiembre'")


    dias_germinacion = models.PositiveIntegerField(null=True, blank=True)
    dias_cosecha = models.PositiveIntegerField(null=True, blank=True)
    imagen = models.ImageField(upload_to='cultivos/', blank=True, null=True)

    class Meta:
        ordering = ['nombre']        # Los cultivos se ordenan alfabéticamente por defecto
        verbose_name = 'Cultivo'
        verbose_name_plural = 'Cultivos'


    def save(self, *args, **kwargs):
        """Genera el slug automáticamente a partir del nombre si no existe."""
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.nombre



# MODELO ENFERMEDAD
# Catálogo de enfermedades detectables por el modelo IA. Cargado con enfermedades.json

class Enfermedad(models.Model):
    """Catálogo de enfermedades que el modelo IA puede detectar."""

    GRAVEDAD_CHOICES = [
        ('leve', 'Leve'),
        ('moderada', 'Moderada'),
        ('grave', 'Grave'),
    ]

    nombre = models.CharField(max_length=150, unique=True)
    nombre_modelo = models.CharField(
        max_length=150,
        unique=True,
        help_text="Nombre exacto que devuelve el modelo de IA"
    )


    descripcion = models.TextField()
    sintomas = models.TextField()
    tratamiento = models.TextField()
    gravedad = models.CharField(max_length=10, choices=GRAVEDAD_CHOICES, default='moderada')
    cultivos_afectados = models.ManyToManyField(Cultivo, blank=True, related_name='enfermedades')


    class Meta:
        ordering = ['nombre']
        verbose_name = 'Enfermedad'
        verbose_name_plural = 'Enfermedades'

    def __str__(self):
        return self.nombre


# MODELO HUERTO
# Cada usuario puede tener varios huertos

class Huerto(models.Model):
    """El huerto de un usuario."""

    UBICACION_CHOICES = [
        ('balcon', 'Balcón'),
        ('terraza', 'Terraza'),
        ('jardin', 'Jardín'),
        ('parcela', 'Parcela'),
        ('interior', 'Interior'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='huertos')


    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True)
    ubicacion = models.CharField(max_length=10, choices=UBICACION_CHOICES)
    codigo_postal = models.CharField(max_length=5, blank=True)


    municipio = models.CharField(max_length=100, blank=True)
    superficie_m2 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)


    class Meta:
        ordering = ['-fecha_creacion']   # Los más recientes primero
        verbose_name = 'Huerto'
        verbose_name_plural = 'Huertos'

    def save(self, *args, **kwargs):
        """Genera el slug a partir del nombre. Incluye el ID para evitar duplicados."""
        if not self.slug:
            base = slugify(self.nombre)
            # Guardamos primero para tener el pk disponible
            super().save(*args, **kwargs)
            self.slug = f"{base}-{self.pk}"
            # Segunda pasada solo para actualizar el slug
            Huerto.objects.filter(pk=self.pk).update(slug=self.slug)
            return
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.nombre} ({self.usuario.username})"


# MODELO SIEMBRA
# Cada siembra registra un cultivo concreto plantado en un huerto

class Siembra(models.Model):
    """Una siembra concreta dentro de un huerto."""

    ESTADO_CHOICES = [
        ('planificada', 'Planificada'),
        ('sembrada', 'Sembrada'),
        ('crecimiento', 'En crecimiento'),
        ('cosechada', 'Cosechada'),
        ('perdida', 'Perdida'),
    ]


    huerto = models.ForeignKey(Huerto, on_delete=models.CASCADE, related_name='siembras')
    cultivo = models.ForeignKey(Cultivo, on_delete=models.PROTECT)


    fecha_siembra = models.DateField()
    fecha_cosecha_estimada = models.DateField(null=True, blank=True)
    fecha_cosecha_real = models.DateField(null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1, help_text="Número de plantas")
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='sembrada')
    notas = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_siembra']   # Las siembras más recientes primero
        verbose_name = 'Siembra'
        verbose_name_plural = 'Siembras'

    def __str__(self):
        return f"{self.cultivo.nombre} en {self.huerto.nombre}"


# MODELO DIAGNOSTICO
# Registro de cada análisis de IA realizado sobre una foto de planta

class Diagnostico(models.Model):
    """Registro de cada diagnóstico de enfermedad realizado por IA."""

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diagnosticos')
    siembra = models.ForeignKey(Siembra, on_delete=models.SET_NULL, null=True, blank=True, related_name='diagnosticos')


    imagen = models.ImageField(upload_to='diagnosticos/')
    enfermedad_detectada = models.ForeignKey(Enfermedad, on_delete=models.SET_NULL, null=True, blank=True)


    confianza = models.DecimalField(max_digits=5, decimal_places=2, help_text="Porcentaje 0-100")
    es_planta_valida = models.BooleanField(default=True, help_text="Si Rekognition validó que es una planta")
    fecha = models.DateTimeField(auto_now_add=True)
    notas_usuario = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']   # Los diagnósticos más recientes primero
        verbose_name = 'Diagnóstico'
        verbose_name_plural = 'Diagnósticos'

    def __str__(self):
        if self.enfermedad_detectada:
            return f"{self.enfermedad_detectada.nombre} ({self.confianza}%)"
        return f"Diagnóstico {self.fecha}"


# MODELO INCIDENCIA
# Notas manuales del usuario sobre problemas en sus siembras

class Incidencia(models.Model):
    """Notas e incidencias del usuario sobre sus siembras."""

    TIPO_CHOICES = [
        ('plaga', 'Plaga'),
        ('enfermedad', 'Enfermedad'),
        ('clima', 'Climática'),
        ('nutricion', 'Nutrición'),
        ('otro', 'Otra'),
    ]

    siembra = models.ForeignKey(Siembra, on_delete=models.CASCADE, related_name='incidencias')
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    fecha = models.DateField()
    resuelto = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha}"
