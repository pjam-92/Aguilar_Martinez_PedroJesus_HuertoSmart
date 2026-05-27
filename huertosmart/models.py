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

"""¡! Explicación (imports):
- models: módulo de Django que contiene todos los tipos de campo (CharField,
  IntegerField, ForeignKey, etc.) y la clase base Model.
- User: el modelo de usuario que Django incluye por defecto. No lo creamos
  nosotros, lo importamos directamente de Django.
- slugify: función de Django que convierte un texto en formato slug (sin
  tildes, sin espacios, todo en minúsculas). Por ejemplo: 'Judía verde'
  se convierte en 'judia-verde'."""


# MODELO CULTIVO
# Catálogo de cultivos disponibles. Los 20 registros se cargan con el fixture cultivos.json

class Cultivo(models.Model):
    """Biblioteca de cultivos disponibles en la plataforma."""

    """¡! Explicación (CHOICES): Los campos con CHOICES limitan los valores
    posibles a una lista predefinida. Se definen como listas de tuplas donde
    el primer elemento es el valor que se guarda en la base de datos (corto)
    y el segundo es el texto legible que se muestra al usuario."""

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

    """¡! Explicación (slug): El slug es la versión del nombre apta para URLs.
    blank=True significa que al crear el objeto no hace falta rellenarlo,
    porque se genera automáticamente en el método save() que ves más abajo.
    unique=True garantiza que no haya dos cultivos con el mismo slug."""

    nombre_cientifico = models.CharField(max_length=150, blank=True)
    descripcion = models.TextField()
    dificultad = models.CharField(max_length=10, choices=DIFICULTAD_CHOICES)
    exposicion = models.CharField(max_length=15, choices=EXPOSICION_CHOICES)
    riego = models.CharField(max_length=10, choices=RIEGO_CHOICES)
    meses_siembra = models.CharField(max_length=50, help_text="Ej: 'marzo,abril,mayo'")
    meses_cosecha = models.CharField(max_length=50, help_text="Ej: 'julio,agosto,septiembre'")

    """¡! Explicación (meses como texto CSV): Los meses se guardan como texto
    separado por comas en lugar de una relación en base de datos, por simplicidad.
    En views.py se convierten a lista con .split(',') para mostrarlos como
    etiquetas individuales en el template."""

    dias_germinacion = models.PositiveIntegerField(null=True, blank=True)
    dias_cosecha = models.PositiveIntegerField(null=True, blank=True)
    imagen = models.ImageField(upload_to='cultivos/', blank=True, null=True)

    class Meta:
        ordering = ['nombre']        # Los cultivos se ordenan alfabéticamente por defecto
        verbose_name = 'Cultivo'
        verbose_name_plural = 'Cultivos'

    """¡! Explicación (class Meta): La clase Meta dentro de un modelo permite
    configurar comportamiento extra. ordering define el orden por defecto cuando
    se consultan los cultivos. verbose_name es el nombre que aparece en el
    panel de administración de Django."""

    def save(self, *args, **kwargs):
        """Genera el slug automáticamente a partir del nombre si no existe."""
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    """¡! Explicación (método save): Al sobreescribir save() podemos ejecutar
    código propio justo antes de que Django guarde el objeto en la base de datos.
    Aquí comprobamos si el slug está vacío y lo generamos con slugify().
    super().save() llama al save() original de Django para que haga el guardado real."""

    def __str__(self):
        return self.nombre

    """¡! Explicación (__str__): Este método define cómo se representa el objeto
    como texto. Django lo usa en el panel de administración y en los selectores
    de formularios. Sin él, los cultivos aparecerían como 'Cultivo object (1)'."""


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

    """¡! Explicación (nombre_modelo): El modelo de IA (MobileNetV2 de Hugging Face)
    devuelve nombres de clase en formato PlantVillage, como 'Tomato___Early_blight'.
    Este campo guarda ese nombre exacto para que el repositorio pueda buscar la
    enfermedad correspondiente cuando el modelo devuelve un resultado."""

    descripcion = models.TextField()
    sintomas = models.TextField()
    tratamiento = models.TextField()
    gravedad = models.CharField(max_length=10, choices=GRAVEDAD_CHOICES, default='moderada')
    cultivos_afectados = models.ManyToManyField(Cultivo, blank=True, related_name='enfermedades')

    """¡! Explicación (ManyToManyField): Una enfermedad puede afectar a varios
    cultivos, y un cultivo puede tener varias enfermedades. ManyToMany crea
    automáticamente una tabla intermedia en la base de datos para gestionar
    esa relación. related_name='enfermedades' permite acceder a las enfermedades
    de un cultivo con cultivo.enfermedades.all()."""

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

    """¡! Explicación (ForeignKey con CASCADE): ForeignKey establece una relación
    de uno a muchos. Un User puede tener muchos Huertos. on_delete=CASCADE significa
    que si se borra el usuario, todos sus huertos se borran también automáticamente.
    related_name='huertos' permite acceder a los huertos de un usuario con
    usuario.huertos.all()."""

    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True)
    ubicacion = models.CharField(max_length=10, choices=UBICACION_CHOICES)
    codigo_postal = models.CharField(max_length=5, blank=True)

    """¡! Explicación (codigo_postal): Se guarda para poder consultar la API de
    AEMET y obtener la previsión meteorológica de la zona del huerto. Es opcional
    (blank=True), si el usuario no lo rellena simplemente no se muestran alertas
    climáticas en el detalle del huerto."""

    municipio = models.CharField(max_length=100, blank=True)
    superficie_m2 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    """¡! Explicación (activo — soft delete): En lugar de borrar el huerto de
    la base de datos, se marca como inactivo (activo=False). Esto se llama
    'soft delete' o borrado lógico. Permite recuperar datos si hubiera un error,
    y mantiene la integridad de los datos históricos."""

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

    """¡! Explicación (slug con ID): A diferencia del Cultivo, el slug del Huerto
    incluye el ID (pk) al final para evitar duplicados. Si dos usuarios crean un
    huerto llamado 'Mi huerto', los slugs serán 'mi-huerto-1' y 'mi-huerto-2'.
    Por eso necesitamos guardar primero (para obtener el pk) y luego actualizar
    el slug en una segunda pasada."""

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

    """¡! Explicación (ESTADO_CHOICES en Siembra): El ciclo de vida de una siembra
    pasa por estos estados. Se usan para filtrar las siembras en el panel del
    huerto (requisito 5 del curso: visualización de datos mediante filtros).
    El método get_estado_display() de Django devuelve el texto legible del estado."""

    huerto = models.ForeignKey(Huerto, on_delete=models.CASCADE, related_name='siembras')
    cultivo = models.ForeignKey(Cultivo, on_delete=models.PROTECT)

    """¡! Explicación (on_delete=PROTECT en cultivo): A diferencia del huerto
    (CASCADE), aquí usamos PROTECT. Esto significa que si alguien intenta borrar
    un cultivo del catálogo que tiene siembras asociadas, Django lo impedirá y
    lanzará un error. Así protegemos la integridad de los datos históricos."""

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

    """¡! Explicación (SET_NULL en siembra): Si se borra una siembra, el diagnóstico
    no se borra — simplemente pierde la referencia a esa siembra (siembra=None).
    Esto es diferente a CASCADE (borrar todo) y a PROTECT (impedir el borrado).
    SET_NULL es la opción correcta cuando queremos conservar el diagnóstico aunque
    desaparezca la siembra a la que estaba vinculado."""

    imagen = models.ImageField(upload_to='diagnosticos/')
    enfermedad_detectada = models.ForeignKey(Enfermedad, on_delete=models.SET_NULL, null=True, blank=True)

    """¡! Explicación (enfermedad nullable): La enfermedad puede ser null porque
    el modelo de IA puede no encontrar coincidencia en el catálogo de enfermedades,
    o porque el resultado fue rechazado por baja confianza. En esos casos el
    diagnóstico se guarda igualmente pero sin enfermedad asociada."""

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

    """¡! Explicación (auto_now_add): auto_now_add=True hace que Django rellene
    automáticamente este campo con la fecha y hora actual en el momento en que
    se crea el objeto. No se puede modificar después. Es diferente a auto_now=True,
    que actualiza la fecha cada vez que se guarda el objeto."""

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha}"
