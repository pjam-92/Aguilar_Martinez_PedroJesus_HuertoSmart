"""
Servicio de Inteligencia Artificial para diagnóstico de enfermedades de plantas.

Utiliza el modelo MobileNetV2 preentrenado sobre el dataset PlantVillage,
disponible en Hugging Face. El procesador se carga manualmente porque el
modelo es anterior al campo image_processor_type y las versiones recientes
de transformers no lo reconocen automáticamente con AutoImageProcessor.
"""
try:
    from transformers import MobileNetV2ImageProcessor, AutoModelForImageClassification
    from PIL import Image
    import torch
    import io
    LIBRERIAS_DISPONIBLES = True
except ImportError:
    LIBRERIAS_DISPONIBLES = False


class DiagnosticoIAService:
    """Servicio para diagnosticar enfermedades en plantas mediante visión por computador."""

    MODEL_NAME = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"

    def __init__(self):
        if not LIBRERIAS_DISPONIBLES:
            raise ImportError(
                "Librerías de IA no disponibles. "
                "Ejecuta: pip install transformers torch torchvision Pillow"
            )
        # Carga explícita con MobileNetV2ImageProcessor en lugar de AutoImageProcessor
        self.processor = MobileNetV2ImageProcessor.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForImageClassification.from_pretrained(self.MODEL_NAME)
        self.model.eval()

    def diagnosticar(self, imagen_bytes):
        """Analiza una imagen y devuelve la enfermedad detectada con su confianza.

        Args:
            imagen_bytes: contenido binario de la imagen (bytes).

        Returns:
            dict con 'nombre_clase', 'confianza' y 'top_5'.
        """
        imagen = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")
        inputs = self.processor(images=imagen, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)

        probabilidades = torch.softmax(outputs.logits, dim=-1)[0]
        idx_predicho = torch.argmax(probabilidades).item()
        nombre_clase = self.model.config.id2label[idx_predicho]
        confianza = round(probabilidades[idx_predicho].item() * 100, 2)

        top5_indices = torch.topk(probabilidades, 5).indices.tolist()
        top5 = [
            {
                'nombre_clase': self.model.config.id2label[idx],
                'confianza': round(probabilidades[idx].item() * 100, 2)
            }
            for idx in top5_indices
        ]

        return {
            'nombre_clase': nombre_clase,
            'confianza': confianza,
            'top_5': top5,
        }


# SINGLETON
_servicio_ia = None


def get_servicio_ia():
    """Devuelve la instancia única del servicio. Se inicializa una sola vez."""
    global _servicio_ia
    if _servicio_ia is None:
        _servicio_ia = DiagnosticoIAService()
    return _servicio_ia
