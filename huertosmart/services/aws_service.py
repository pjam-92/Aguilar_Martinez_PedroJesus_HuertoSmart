# aws_service.py — Servicio de validación de imágenes con AWS Rekognition
"""
Este archivo implementa la conexión con Amazon Web Services (AWS) Rekognition,
un servicio de visión por computador en la nube que permite analizar imágenes
automáticamente.

En HuertoSmart, Rekognition se usa como primer filtro antes del diagnóstico:
comprueba que la imagen subida por el usuario efectivamente contiene una planta.
Si no es una planta, se rechaza la imagen antes de gastar tiempo y recursos
en el modelo de IA.

Las credenciales de AWS se leen del archivo .env y nunca se escriben
directamente en el código. El límite gratuito de Rekognition es 1.000
peticiones al mes, suficiente para este proyecto.

Si AWS no está disponible o falla, el diagnóstico continúa igualmente
sin la validación previa.
"""

import io
import os

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_DISPONIBLE = True
except ImportError:
    BOTO3_DISPONIBLE = False

"""¡! Explicación (boto3): boto3 es la librería oficial de Python para interactuar
con todos los servicios de AWS. ClientError es la excepción que lanza boto3
cuando AWS devuelve un error (credenciales inválidas, límite superado, etc.)."""

try:
    from PIL import Image as PILImage
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False


# FUNCIÓN AUXILIAR DE CONVERSIÓN DE IMÁGENES

def convertir_a_jpeg(imagen_bytes):
    """Convierte cualquier formato de imagen a JPEG en memoria.

    Rekognition solo acepta JPEG y PNG. Esta función garantiza compatibilidad
    convirtiendo WEBP, TIFF y otros formatos antes de enviar a AWS.
    Si PIL no está disponible, devuelve los bytes originales sin convertir.
    """
    if not PIL_DISPONIBLE:
        return imagen_bytes
    try:
        img = PILImage.open(io.BytesIO(imagen_bytes)).convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        return buffer.getvalue()
    except Exception:
        return imagen_bytes

"""¡! Explicación (convertir_a_jpeg): Los usuarios pueden subir imágenes en
cualquier formato: JPG, PNG, WEBP, HEIC, etc. AWS Rekognition solo acepta
JPEG y PNG. Esta función convierte cualquier formato a JPEG usando Pillow
antes de enviar la imagen a AWS. Si la conversión falla, devuelve la imagen
original y dejamos que AWS decida si puede procesarla."""


class AWSService:
    """Cliente para servicios de AWS utilizados por HuertoSmart."""

    def __init__(self):
        """Inicializa el cliente de Rekognition con las credenciales del .env."""
        if not BOTO3_DISPONIBLE:
            raise ImportError("boto3 no instalado. Ejecuta: pip install boto3")

        self.region_rekognition = os.getenv('AWS_REKOGNITION_REGION', 'eu-west-1')

        """¡! Explicación (os.getenv): Lee variables del archivo .env que fueron
        cargadas al arrancar Django gracias a python-dotenv. Si la variable no
        existe, usa el valor por defecto indicado (en este caso 'eu-west-1',
        la región de Irlanda). Las credenciales nunca se escriben en el código."""

        # Creamos el cliente de Rekognition con las credenciales del entorno
        self.rekognition_client = boto3.client(
            'rekognition',
            region_name=self.region_rekognition,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )

    def validar_es_planta(self, imagen_bytes, umbral_confianza=70):
        """Usa Rekognition DetectLabels para validar que la imagen contiene una planta.

        Rekognition analiza la imagen y devuelve una lista de etiquetas con su
        porcentaje de confianza. Comprobamos si alguna etiqueta corresponde
        a elementos vegetales.

        Returns:
            dict con 'es_planta' (bool), 'etiquetas' (list) y 'mensaje' (str).
        """
        try:
            # Convertimos a JPEG para garantizar compatibilidad con Rekognition
            imagen_jpeg = convertir_a_jpeg(imagen_bytes)

            # Llamamos al API de Rekognition
            response = self.rekognition_client.detect_labels(
                Image={'Bytes': imagen_jpeg},
                MaxLabels=10,           # Máximo de etiquetas a devolver
                MinConfidence=umbral_confianza,  # Solo etiquetas con más del 70% de confianza
            )

            """¡! Explicación (detect_labels): Este método de Rekognition analiza
            la imagen y devuelve una lista de etiquetas en inglés con su porcentaje
            de confianza. Por ejemplo, para una foto de un tomate podría devolver:
            [{'Name': 'Plant', 'Confidence': 98.5}, {'Name': 'Tomato', 'Confidence': 94.2}, ...]"""

            # Etiquetas que consideramos indicativas de que hay una planta en la imagen
            etiquetas_objetivo = {'Leaf', 'Plant', 'Vegetation', 'Flower', 'Tree', 'Herb'}

            etiquetas_encontradas = [
                {'nombre': label['Name'], 'confianza': round(label['Confidence'], 2)}
                for label in response['Labels']
            ]

            # Comprobamos si alguna etiqueta detectada está en nuestra lista objetivo
            es_planta = any(
                label['Name'] in etiquetas_objetivo
                for label in response['Labels']
            )

            """¡! Explicación (any()): La función any() devuelve True si al menos
            uno de los elementos del iterable es verdadero. Aquí comprobamos si
            alguna de las etiquetas devueltas por Rekognition está en el conjunto
            etiquetas_objetivo. Es más eficiente que un bucle for con un if."""

            mensaje = (
                "Imagen válida: contiene elementos vegetales."
                if es_planta
                else "La imagen no parece contener una planta. Sube una foto clara de una hoja."
            )

            return {
                'es_planta': es_planta,
                'etiquetas': etiquetas_encontradas,
                'mensaje': mensaje,
            }

        except ClientError as e:
            # Si Rekognition falla, no bloqueamos el diagnóstico — dejamos pasar
            return {
                'es_planta': True,
                'etiquetas': [],
                'mensaje': 'Validación previa no disponible.',
            }

        """¡! Explicación (fallback en ClientError): Si AWS devuelve un error
        (credenciales inválidas, límite de peticiones superado, sin conexión),
        en lugar de mostrar un error al usuario devolvemos es_planta=True para
        que el diagnóstico continúe igualmente sin la validación de Rekognition."""


# PATRÓN SINGLETON — Una sola instancia del cliente AWS para toda la aplicación

_aws_service = None


def get_aws_service():
    """Devuelve la instancia única del servicio AWS. Se inicializa solo la primera vez."""
    global _aws_service
    if _aws_service is None:
        _aws_service = AWSService()
    return _aws_service
