# aemet_service.py — Servicio meteorológico con la API OpenData de AEMET
"""
Este archivo implementa la conexión con la API OpenData de AEMET
(Agencia Estatal de Meteorología de España) para obtener la previsión
meteorológica de la zona donde está ubicado cada huerto.

Flujo completo del servicio:
1. A partir del código postal del huerto, buscamos el municipio AEMET más cercano.
2. Consultamos la predicción diaria a 7 días para ese municipio.
3. Analizamos los datos y generamos alertas si detectamos condiciones
   de riesgo para el huerto (heladas, calor extremo, lluvia intensa, viento fuerte).

La API de AEMET es gratuita pero requiere registro para obtener una API key.
Funciona en dos pasos: primero se obtiene una URL de datos, luego se descarga
el JSON desde esa URL. Este diseño en dos pasos es propio de AEMET.

Este servicio se llama desde views.py en la vista detalle_huerto,
dentro de un try/except para que si falla no derribe la página.
"""

import os
import json
import logging
import urllib.request
import urllib.error

"""¡! Explicación (urllib en lugar de requests): Usamos urllib de la librería
estándar de Python en lugar de la librería requests porque ya está instalada
sin necesidad de dependencias adicionales. Para llamadas sencillas como estas
es suficiente."""

logger = logging.getLogger(__name__)

# URL base de la API OpenData de AEMET
BASE_URL = 'https://opendata.aemet.es/opendata/api'

# UMBRALES DE ALERTA — valores a partir de los cuales se genera una alerta para el huerto
UMBRAL_HELADA = 2        # °C — temperatura mínima bajo la que hay riesgo de helada
UMBRAL_CALOR = 35        # °C — temperatura máxima sobre la que hay riesgo de golpe de calor
UMBRAL_LLUVIA = 30       # mm — precipitación diaria que se considera intensa
UMBRAL_VIENTO = 50       # km/h — viento que puede dañar plantas

"""¡! Explicación (umbrales como constantes): Definir los umbrales como constantes
al inicio del archivo permite ajustarlos fácilmente sin buscar números sueltos
por el código. Si el agrónomo dice que las heladas son peligrosas a partir de 0°C
en lugar de 2°C, solo hay que cambiar una línea."""


# FUNCIONES INTERNAS DE COMUNICACIÓN CON LA API

def _get(url):
    """Realiza una petición GET autenticada a la API de AEMET y devuelve el JSON.

    Añade automáticamente la API key como parámetro en la URL.
    Devuelve None si la petición falla.
    """
    api_key = os.getenv('AEMET_API_KEY', '')
    separador = '&' if '?' in url else '?'
    url_completa = f"{url}{separador}api_key={api_key}"

    """¡! Explicación (API key en la URL): La API de AEMET requiere autenticación
    mediante una clave que se añade como parámetro en la URL. La clave se lee del
    archivo .env con os.getenv() para no escribirla en el código. El separador
    '?' o '&' se elige según si la URL ya tiene otros parámetros o no."""

    try:
        req = urllib.request.Request(url_completa, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        logger.warning(f"Error AEMET GET {url}: {e}")
        return None


def _get_datos(url_datos):
    """Descarga el JSON de datos desde la URL secundaria que devuelve AEMET.

    La API de AEMET funciona en dos pasos: la primera llamada devuelve una URL
    donde están los datos reales. Esta función descarga esos datos.
    Usa latin-1 porque AEMET devuelve caracteres con ese encoding.
    """
    try:
        req = urllib.request.Request(url_datos, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('latin-1'))
    except Exception as e:
        logger.warning(f"Error descargando datos AEMET: {e}")
        return None

"""¡! Explicación (diseño en dos pasos de AEMET): La API de AEMET tiene un diseño
particular. Cuando llamas a un endpoint, no devuelve los datos directamente sino
una respuesta JSON con una URL ('datos') donde están los datos reales. Hay que
hacer una segunda petición a esa URL para obtener la predicción. Esto es propio
de AEMET y hay que tenerlo en cuenta al usar su API."""


# FUNCIÓN DE BÚSQUEDA DE MUNICIPIO

def buscar_municipio_por_cp(codigo_postal):
    """Busca el ID de municipio AEMET más cercano a un código postal dado.

    AEMET no tiene endpoint directo por código postal, así que usamos los primeros
    dos dígitos (código de provincia) para filtrar la lista completa de municipios
    y devolvemos el primero de esa provincia como aproximación.

    Returns:
        str: ID de municipio AEMET (ej. '30030') o None si no se encuentra.
    """
    if not codigo_postal or len(codigo_postal) < 2:
        return None

    # Obtenemos la lista completa de municipios de España
    resultado = _get(f"{BASE_URL}/maestro/municipios")
    if not resultado or resultado.get('estado') != 200:
        return None

    url_datos = resultado.get('datos')
    if not url_datos:
        return None

    municipios = _get_datos(url_datos)
    if not municipios:
        return None

    """¡! Explicación (lista de municipios): AEMET proporciona un endpoint con
    todos los municipios de España y sus IDs. Descargamos esta lista cada vez
    porque no tenemos una base de datos local de municipios. En un proyecto
    en producción, esta lista se cachearía para no descargarla en cada petición."""

    # Los primeros dos dígitos del CP corresponden a la provincia
    provincia = codigo_postal[:2]

    # Filtramos los municipios de esa provincia por su código INE
    candidatos = [
        m for m in municipios
        if m.get('id', '').replace('id', '')[:2] == provincia
    ]

    """¡! Explicación (código INE y AEMET): Los IDs de municipio en AEMET tienen
    formato 'id30030' donde 30030 es el código INE del municipio. Los primeros
    dos dígitos del código INE corresponden a la provincia (30 = Murcia, 28 = Madrid,
    08 = Barcelona, etc.). Los primeros dos dígitos del código postal también
    indican la provincia, así que podemos usarlos para filtrar."""

    if not candidatos:
        return municipios[0].get('id', '').replace('id', '') if municipios else None

    # Devolvemos el primer municipio de la provincia como aproximación al CP
    return candidatos[0].get('id', '').replace('id', '')


# FUNCIÓN DE OBTENCIÓN DE PREDICCIÓN

def obtener_prediccion(id_municipio):
    """Obtiene la predicción diaria a 7 días para un municipio AEMET.

    Returns:
        list: Lista de dicts con los datos meteorológicos de cada día,
              o lista vacía si la consulta falla.
    """
    resultado = _get(f"{BASE_URL}/prediccion/especifica/municipio/diaria/{id_municipio}")
    if not resultado or resultado.get('estado') != 200:
        return []

    url_datos = resultado.get('datos')
    if not url_datos:
        return []

    datos = _get_datos(url_datos)
    if not datos or not isinstance(datos, list):
        return []

    try:
        # La predicción está anidada dentro de la estructura JSON de AEMET
        prediccion = datos[0]['prediccion']['dia']
        dias = []

        for dia in prediccion[:7]:   # Tomamos solo los 7 primeros días
            fecha = dia.get('fecha', '')[:10]   # Solo la parte de fecha (YYYY-MM-DD)

            # Temperatura máxima y mínima del día
            temp_max = None
            temp_min = None
            temps = dia.get('temperatura', {})
            if isinstance(temps, dict):
                temp_max = temps.get('maxima')
                temp_min = temps.get('minima')

            # Precipitación: tomamos el valor máximo de todos los periodos del día
            lluvia = 0
            precips = dia.get('precipitacion', [])
            if isinstance(precips, list):
                valores = [p.get('value', 0) for p in precips if p.get('value') not in (None, '')]
                if valores:
                    try:
                        lluvia = max(float(v) for v in valores)
                    except (ValueError, TypeError):
                        lluvia = 0

            """¡! Explicación (precipitación por periodos): AEMET divide el día en
            varios periodos (mañana, tarde, noche) y da la precipitación de cada uno.
            Tomamos el máximo para saber cuál es el peor escenario del día completo."""

            # Viento: velocidad máxima del día entre todos los periodos
            viento = 0
            vientos = dia.get('viento', [])
            if isinstance(vientos, list):
                velocidades = [v.get('velocidad', 0) for v in vientos if v.get('velocidad') not in (None, '')]
                if velocidades:
                    try:
                        viento = max(float(v) for v in velocidades)
                    except (ValueError, TypeError):
                        viento = 0

            # Estado del cielo: descripción del primer periodo del día
            cielo = ''
            cielos = dia.get('estadoCielo', [])
            if isinstance(cielos, list) and cielos:
                cielo = cielos[0].get('descripcion', '')

            dias.append({
                'fecha': fecha,
                'temp_max': temp_max,
                'temp_min': temp_min,
                'lluvia': lluvia,
                'viento': viento,
                'cielo': cielo,
            })

        return dias

    except (KeyError, IndexError, TypeError) as e:
        logger.warning(f"Error parseando predicción AEMET: {e}")
        return []


# FUNCIÓN DE DETECCIÓN DE ALERTAS

def detectar_alertas(dias):
    """Analiza los días de predicción y genera alertas de riesgo para el huerto.

    Compara los valores meteorológicos con los umbrales definidos al inicio
    del archivo y genera una alerta por cada condición de riesgo detectada.

    Returns:
        list: Lista de dicts con 'tipo', 'icono', 'mensaje', 'fecha' y 'nivel'.
              'nivel' puede ser 'warning' (precaución) o 'danger' (peligro).
    """
    alertas = []

    for dia in dias:
        fecha = dia['fecha']
        temp_min = dia.get('temp_min')
        temp_max = dia.get('temp_max')
        lluvia = dia.get('lluvia', 0)
        viento = dia.get('viento', 0)

        try:
            # Alerta de helada — nivel danger porque puede matar las plantas
            if temp_min is not None and float(temp_min) <= UMBRAL_HELADA:
                alertas.append({
                    'tipo': 'helada',
                    'icono': '🧊',
                    'mensaje': f"Riesgo de helada: temperatura mínima de {temp_min}°C",
                    'fecha': fecha,
                    'nivel': 'danger',
                })

            # Alerta de calor extremo — nivel warning, riesgo de estrés hídrico
            if temp_max is not None and float(temp_max) >= UMBRAL_CALOR:
                alertas.append({
                    'tipo': 'calor',
                    'icono': '🌡',
                    'mensaje': f"Ola de calor: temperatura máxima de {temp_max}°C",
                    'fecha': fecha,
                    'nivel': 'warning',
                })

            # Alerta de lluvia intensa — puede causar encharcamiento o erosión
            if lluvia and float(lluvia) >= UMBRAL_LLUVIA:
                alertas.append({
                    'tipo': 'lluvia',
                    'icono': '🌧',
                    'mensaje': f"Lluvia intensa prevista: {lluvia} mm",
                    'fecha': fecha,
                    'nivel': 'warning',
                })

            # Alerta de viento fuerte — puede dañar plantas frágiles o tutores
            if viento and float(viento) >= UMBRAL_VIENTO:
                alertas.append({
                    'tipo': 'viento',
                    'icono': '💨',
                    'mensaje': f"Viento fuerte previsto: {viento} km/h",
                    'fecha': fecha,
                    'nivel': 'warning',
                })

        except (ValueError, TypeError):
            # Si un valor no se puede convertir a float, ignoramos ese día
            continue

    return alertas


# FUNCIÓN PRINCIPAL DEL SERVICIO

def get_alertas_huerto(codigo_postal):
    """Función principal: dado un código postal devuelve predicción y alertas.

    Esta es la única función que llama views.py. Internamente coordina
    la búsqueda del municipio, la obtención de la predicción y la detección
    de alertas.

    Returns:
        dict con 'prediccion' (list de días), 'alertas' (list de alertas)
        y 'municipio_id' (str). Si cualquier paso falla, devuelve listas vacías.
    """
    municipio_id = buscar_municipio_por_cp(codigo_postal)
    if not municipio_id:
        return {'prediccion': [], 'alertas': [], 'municipio_id': None}

    prediccion = obtener_prediccion(municipio_id)
    alertas = detectar_alertas(prediccion)

    return {
        'prediccion': prediccion,
        'alertas': alertas,
        'municipio_id': municipio_id,
    }
