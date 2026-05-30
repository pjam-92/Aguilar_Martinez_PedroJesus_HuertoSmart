# ia_service.py — Servicio de Inteligencia Artificial para diagnóstico de plantas
"""
Este archivo implementa el servicio de diagnóstico de enfermedades mediante
visión por computador. Es una de las funcionalidades principales del proyecto
CE-IABD (Inteligencia Artificial y Big Data).

Utiliza el modelo MobileNetV2 preentrenado sobre el dataset PlantVillage,
disponible gratuitamente en Hugging Face. El modelo puede identificar 38
clases de enfermedades en plantas de cultivo comunes.

El procesador se carga manualmente con MobileNetV2ImageProcessor porque
el modelo es anterior al campo image_processor_type y las versiones
recientes de transformers no lo reconocen automáticamente con
AutoImageProcessor.

Este servicio se llama desde views.py en la vista diagnostico_nuevo,
dentro de un bloque try/except para que si falla no derribe toda la app.
"""

# Importamos las librerías de IA dentro de un try/except porque son opcionales
# Si no están instaladas, el resto de la app sigue funcionando igualmente
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

    # Nombre del modelo en Hugging Face — se descarga automáticamente la primera vez
    MODEL_NAME = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"

    def __init__(self):
        """Carga el modelo y el procesador de imágenes desde Hugging Face."""
        if not LIBRERIAS_DISPONIBLES:
            raise ImportError(
                "Librerías de IA no disponibles. "
                "Ejecuta: pip install transformers torch torchvision Pillow"
            )

        # Carga explícita con MobileNetV2ImageProcessor en lugar de AutoImageProcessor
        self.processor = MobileNetV2ImageProcessor.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForImageClassification.from_pretrained(self.MODEL_NAME)

        # Ponemos el modelo en modo evaluación — desactiva el dropout y otras capas
        # de entrenamiento que no se necesitan para hacer predicciones
        self.model.eval()

    def diagnosticar(self, imagen_bytes):
        """Analiza una imagen y devuelve la enfermedad detectada con su confianza.

        Args:
            imagen_bytes: contenido binario de la imagen (bytes).

        Returns:
            dict con 'nombre_clase', 'confianza' y 'top_5'.
        """

        # Convertimos los bytes a una imagen PIL en formato RGB
        imagen = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")

        # El procesador prepara la imagen para el modelo: la redimensiona a 224x224,
        # la normaliza y la convierte a tensores de PyTorch
        inputs = self.processor(images=imagen, return_tensors="pt")

        # Ejecutamos el modelo sin calcular gradientes (más rápido, menos memoria)
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Convertimos los logits a probabilidades con softmax
        probabilidades = torch.softmax(outputs.logits, dim=-1)[0]

        # Obtenemos el índice de la clase con mayor probabilidad
        idx_predicho = torch.argmax(probabilidades).item()

        # Traducimos el índice al nombre de la clase usando el mapa del modelo
        nombre_clase = self.model.config.id2label[idx_predicho]
        confianza = round(probabilidades[idx_predicho].item() * 100, 2)

        # Calculamos también el top 5 de enfermedades más probables
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

# PATRÓN SINGLETON — Una sola instancia del servicio para toda la aplicación

_servicio_ia = None

def get_servicio_ia():
    """Devuelve la instancia única del servicio de IA. Se inicializa solo la primera vez."""
    global _servicio_ia
    if _servicio_ia is None:
        _servicio_ia = DiagnosticoIAService()
    return _servicio_ia
