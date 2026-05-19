# HuertoSmart
Plataforma web para ayudar a gestionar un huerto doméstico. Permite diagnosticar enfermedades de plantas mediante inteligencia artificial, consultar información sobre cultivos y hacer seguimiento de las siembras.

Proyecto Fin de Curso — Curso de Especialización en Inteligencia Artificial y Big Data.
Autor: Pedro Jesús Aguilar Martínez
Centro: MEDAC / Davante
Curso: 2025-2026

## Qué hace la aplicación
- Sube una foto de una planta y el sistema la analiza con un modelo de IA para detectar posibles enfermedades.
- Consulta una biblioteca de 20 cultivos con información detallada y filtros.
- Gestiona tus huertos y registra siembras con su estado y seguimiento.
- Ve la previsión meteorológica de tu zona directamente en el panel del huerto.
- Exporta los datos de tus siembras a Excel.
- Inicia sesión con tu cuenta de Google.

## Tecnologías utilizadas
- Python 3.14 y Django 6.0.4
- django-allauth para autenticación con Google (OAuth2)
- Tailwind CSS para el diseño (vía CDN, sin proceso de build)
- Modelo de IA: MobileNetV2 de Hugging Face, entrenado con el dataset PlantVillage
- AWS Rekognition para validar que la imagen subida es una planta
- API de AEMET OpenData para la previsión del tiempo
- openpyxl para exportar a Excel
- SQLite como base de datos

## Instalación

### 1. Clonar el repositorio
```
git clone https://github.com/pjam-92/Aguilar_Martinez_PedroJesus_HuertoSmart.git
cd Aguilar_Martinez_PedroJesus_HuertoSmart
```

### 2. Crear y activar el entorno virtual
```
python -m venv .venv
En Windows: .venv\Scripts\Activate.ps1
En Linux/Mac: source .venv/bin/activate
```

### 3. Instalar dependencias
```
pip install -r requirements.txt
```

### 4. Crear el archivo .env
Crear un archivo `.env` en la raíz con estas variables:
```
SECRET_KEY=una_clave_secreta
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REKOGNITION_REGION=eu-west-1
AEMET_API_KEY=...
```

### 5. Aplicar migraciones y cargar datos
```
python manage.py migrate
python manage.py loaddata cultivos.json enfermedades.json
```

### 6. Crear superusuario
```
python manage.py createsuperuser
```

### 7. Configurar el Site en el admin
Entrar en /admin/ → Sites → cambiar el dominio del site por defecto a `127.0.0.1:8000`. Sin este paso el login con Google no funciona correctamente.

### 8. Arrancar
```
python manage.py runserver
```
Abrir http://127.0.0.1:8000/

## Estructura
```
miproyectodjango/         Configuración del proyecto (settings, urls, wsgi)
huertosmart/              App principal
    repositories/         Patrón Repository (6 repositorios, acceso a BD)
    services/             Servicios externos (IA, AWS Rekognition, AEMET)
    fixtures/             Datos iniciales en JSON (cultivos y enfermedades)
    migrations/           Migraciones de base de datos
    models.py             Modelos: Cultivo, Enfermedad, Huerto, Siembra, Diagnóstico, Incidencia
    views.py              Vistas (usan repositorios, nunca ORM directamente)
    admin.py              Panel de administración personalizado
    urls.py               URLs de la aplicación
    forms.py              Formularios Django
templates/                Plantillas HTML (base, cultivos, huerto, diagnóstico, allauth)
static/                   Imágenes estáticas (cultivos y carrusel de inicio)
ml_models/                Carpeta donde se descarga el modelo de IA (vacía en el repositorio)
```

## Notas
- El modelo de IA se descarga automáticamente de Hugging Face la primera vez que se usa. Necesita conexión a internet. Se almacena en `ml_models/`.
- El login con Google está en modo testing, por lo que solo funciona con el email del desarrollador configurado como usuario de prueba en Google Cloud Console.
- El archivo `.env` no está en el repositorio por seguridad. Debe solicitarse al autor para poder ejecutar el proyecto localmente.
