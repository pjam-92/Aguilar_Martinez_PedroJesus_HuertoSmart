"""
Servicios de AWS: Rekognition para validación de imágenes de plantas.

Las credenciales se leen del archivo .env.
Las imágenes se convierten a JPEG antes de enviarse a Rekognition porque
el servicio no acepta formatos como WEBP o TIFF.
"""
import io
import os

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_DISPONIBLE = True
except ImportError:
    BOTO3_DISPONIBLE = False

try:
    from PIL import Image as PILImage
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False


def convertir_a_jpeg(imagen_bytes):
    """Convierte cualquier formato de imagen a JPEG en memoria.

    Rekognition solo acepta JPEG y PNG. Esta función garantiza compatibilidad
    convirtiendo WEBP, TIFF y otros formatos antes de enviar.
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


class AWSService:
    """Cliente para servicios de AWS utilizados por HuertoSmart."""

    def __init__(self):
        if not BOTO3_DISPONIBLE:
            raise ImportError("boto3 no instalado. Ejecuta: pip install boto3")

        self.region_rekognition = os.getenv('AWS_REKOGNITION_REGION', 'eu-west-1')

        self.rekognition_client = boto3.client(
            'rekognition',
            region_name=self.region_rekognition,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )

    def validar_es_planta(self, imagen_bytes, umbral_confianza=70):
        """Usa Rekognition DetectLabels para validar que la imagen contiene una planta.

        Convierte la imagen a JPEG antes de enviarla para garantizar compatibilidad.

        Returns:
            dict con 'es_planta' (bool), 'etiquetas' (list) y 'mensaje' (str).
        """
        try:
            imagen_jpeg = convertir_a_jpeg(imagen_bytes)

            response = self.rekognition_client.detect_labels(
                Image={'Bytes': imagen_jpeg},
                MaxLabels=10,
                MinConfidence=umbral_confianza,
            )

            etiquetas_objetivo = {'Leaf', 'Plant', 'Vegetation', 'Flower', 'Tree', 'Herb'}
            etiquetas_encontradas = [
                {'nombre': label['Name'], 'confianza': round(label['Confidence'], 2)}
                for label in response['Labels']
            ]

            es_planta = any(
                label['Name'] in etiquetas_objetivo
                for label in response['Labels']
            )

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
            # Si Rekognition falla, no bloqueamos el diagnóstico
            return {
                'es_planta': True,
                'etiquetas': [],
                'mensaje': 'Validación previa no disponible.',
            }


_aws_service = None


def get_aws_service():
    """Devuelve la instancia única del servicio AWS."""
    global _aws_service
    if _aws_service is None:
        _aws_service = AWSService()
    return _aws_service
