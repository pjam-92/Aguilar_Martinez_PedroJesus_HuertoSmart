"""
Servicio de meteorología usando la API OpenData de AEMET.

Flujo:
1. A partir del código postal se busca el municipio en la lista oficial de AEMET.
2. Se consulta la predicción diaria para ese municipio.
3. Se analizan los datos y se generan alertas si se detectan condiciones de riesgo.

Las alertas cubren: heladas, olas de calor, lluvia intensa y viento fuerte.
"""
import os
import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

BASE_URL = 'https://opendata.aemet.es/opendata/api'

# Umbrales para generar alertas
UMBRAL_HELADA = 2        # °C — temperatura mínima bajo la que hay riesgo de helada
UMBRAL_CALOR = 35        # °C — temperatura máxima sobre la que hay riesgo de golpe de calor
UMBRAL_LLUVIA = 30       # mm — precipitación diaria que se considera intensa
UMBRAL_VIENTO = 50       # km/h — viento que puede dañar plantas


def _get(url):
    """Realiza una petición GET a la API de AEMET y devuelve el JSON."""
    api_key = os.getenv('AEMET_API_KEY', '')
    separador = '&' if '?' in url else '?'
    url_completa = f"{url}{separador}api_key={api_key}"

    try:
        req = urllib.request.Request(url_completa, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        logger.warning(f"Error AEMET GET {url}: {e}")
        return None


def _get_datos(url_datos):
    """Descarga el JSON de datos desde la URL secundaria que devuelve AEMET."""
    try:
        req = urllib.request.Request(url_datos, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('latin-1'))
    except Exception as e:
        logger.warning(f"Error descargando datos AEMET: {e}")
        return None


def buscar_municipio_por_cp(codigo_postal):
    """Busca el ID de municipio AEMET más cercano a un código postal.

    AEMET no tiene endpoint directo por CP, así que usamos los primeros
    dos dígitos (provincia) para filtrar la lista de municipios y buscamos
    el que tenga el CP más parecido en su código INE.

    Returns:
        str: ID de municipio AEMET (ej. '30030') o None si no se encuentra.
    """
    if not codigo_postal or len(codigo_postal) < 2:
        return None

    resultado = _get(f"{BASE_URL}/maestro/municipios")
    if not resultado or resultado.get('estado') != 200:
        return None

    url_datos = resultado.get('datos')
    if not url_datos:
        return None

    municipios = _get_datos(url_datos)
    if not municipios:
        return None

    # Los IDs de municipio en AEMET tienen formato "id" con el código INE
    # Los primeros dos dígitos del CP corresponden a la provincia
    provincia = codigo_postal[:2]

    candidatos = [
        m for m in municipios
        if m.get('id', '').replace('id', '')[:2] == provincia
    ]

    if not candidatos:
        # Si no hay candidatos de la provincia, devolvemos el primero de España
        return municipios[0].get('id', '').replace('id', '') if municipios else None

    # Devolvemos el primer municipio de la provincia como aproximación
    return candidatos[0].get('id', '').replace('id', '')


def obtener_prediccion(id_municipio):
    """Obtiene la predicción diaria para un municipio AEMET.

    Returns:
        list: Lista de dicts con datos por día, o lista vacía si falla.
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
        prediccion = datos[0]['prediccion']['dia']
        dias = []
        for dia in prediccion[:7]:
            fecha = dia.get('fecha', '')[:10]

            # Temperatura
            temp_max = None
            temp_min = None
            temps = dia.get('temperatura', {})
            if isinstance(temps, dict):
                temp_max = temps.get('maxima')
                temp_min = temps.get('minima')

            # Precipitación (tomamos el valor máximo del día)
            lluvia = 0
            precips = dia.get('precipitacion', [])
            if isinstance(precips, list):
                valores = [p.get('value', 0) for p in precips if p.get('value') not in (None, '')]
                if valores:
                    try:
                        lluvia = max(float(v) for v in valores)
                    except (ValueError, TypeError):
                        lluvia = 0

            # Viento (velocidad máxima del día)
            viento = 0
            vientos = dia.get('viento', [])
            if isinstance(vientos, list):
                velocidades = [v.get('velocidad', 0) for v in vientos if v.get('velocidad') not in (None, '')]
                if velocidades:
                    try:
                        viento = max(float(v) for v in velocidades)
                    except (ValueError, TypeError):
                        viento = 0

            # Estado del cielo (descripción)
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


def detectar_alertas(dias):
    """Analiza los días de predicción y genera alertas de riesgo para el huerto.

    Returns:
        list: Lista de dicts con 'tipo', 'mensaje', 'fecha' y 'nivel' (warning/danger).
    """
    alertas = []

    for dia in dias:
        fecha = dia['fecha']
        temp_min = dia.get('temp_min')
        temp_max = dia.get('temp_max')
        lluvia = dia.get('lluvia', 0)
        viento = dia.get('viento', 0)

        try:
            if temp_min is not None and float(temp_min) <= UMBRAL_HELADA:
                alertas.append({
                    'tipo': 'helada',
                    'icono': '🧊',
                    'mensaje': f"Riesgo de helada: temperatura mínima de {temp_min}°C",
                    'fecha': fecha,
                    'nivel': 'danger',
                })

            if temp_max is not None and float(temp_max) >= UMBRAL_CALOR:
                alertas.append({
                    'tipo': 'calor',
                    'icono': '🌡',
                    'mensaje': f"Ola de calor: temperatura máxima de {temp_max}°C",
                    'fecha': fecha,
                    'nivel': 'warning',
                })

            if lluvia and float(lluvia) >= UMBRAL_LLUVIA:
                alertas.append({
                    'tipo': 'lluvia',
                    'icono': '🌧',
                    'mensaje': f"Lluvia intensa prevista: {lluvia} mm",
                    'fecha': fecha,
                    'nivel': 'warning',
                })

            if viento and float(viento) >= UMBRAL_VIENTO:
                alertas.append({
                    'tipo': 'viento',
                    'icono': '💨',
                    'mensaje': f"Viento fuerte previsto: {viento} km/h",
                    'fecha': fecha,
                    'nivel': 'warning',
                })

        except (ValueError, TypeError):
            continue

    return alertas


def get_alertas_huerto(codigo_postal):
    """Función principal: dado un CP devuelve predicción y alertas.

    Returns:
        dict con 'prediccion' (list), 'alertas' (list) y 'municipio_id' (str).
        Si falla, devuelve prediccion y alertas vacías.
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
