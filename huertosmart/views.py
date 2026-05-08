import io
import logging

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.templatetags.static import static

from .models import Cultivo, Huerto, Diagnostico, Enfermedad, Siembra
from .forms import CultivoFilterForm, HuertoForm, SiembraForm
from .repositories.cultivo_repository import CultivoRepository
from .repositories.huerto_repository import HuertoRepository
from .repositories.siembra_repository import SiembraRepository
from .repositories.diagnostico_repository import DiagnosticoRepository

logger = logging.getLogger(__name__)

UMBRAL_CONFIANZA_MINIMA = 50

IMAGENES_CULTIVOS = {
    'Tomate':       'img/cultivos/tomate.jpg',
    'Lechuga':      'img/cultivos/lechuga.jpg',
    'Pimiento':     'img/cultivos/pimiento.jpg',
    'Calabacín':    'img/cultivos/calabacin.jpg',
    'Patata':       'img/cultivos/patata.jpg',
    'Zanahoria':    'img/cultivos/zanahoria.jpg',
    'Ajo':          'img/cultivos/ajo.jpg',
    'Cebolla':      'img/cultivos/cebolla.jpg',
    'Espinaca':     'img/cultivos/espinaca.jpg',
    'Acelga':       'img/cultivos/acelga.jpg',
    'Judía verde':  'img/cultivos/judia.jpg',
    'Pepino':       'img/cultivos/pepino.jpg',
    'Berenjena':    'img/cultivos/berenjena.jpg',
    'Rábano':       'img/cultivos/rabano.jpg',
    'Fresa':        'img/cultivos/fresa.jpg',
    'Maíz':         'img/cultivos/maiz.jpg',
    'Manzano':      'img/cultivos/manzano.jpg',
    'Uva':          'img/cultivos/uva.jpg',
    'Melocotonero': 'img/cultivos/melocotonero.jpg',
    'Albahaca':     'img/cultivos/albahaca.jpg',
}


def _imagen_url(nombre):
    ruta = IMAGENES_CULTIVOS.get(nombre, '')
    return static(ruta) if ruta else ''


# PÁGINAS PÚBLICAS

def home(request):
    return render(request, 'huertosmart/home.html')


# F3 - BIBLIOTECA DE CULTIVOS

def lista_cultivos(request):
    """Lista filtrable de cultivos."""
    form = CultivoFilterForm(request.GET or None)
    repo = CultivoRepository()

    if form.is_valid():
        cultivos = repo.filtrar(
            busqueda=form.cleaned_data.get('busqueda'),
            dificultad=form.cleaned_data.get('dificultad'),
            exposicion=form.cleaned_data.get('exposicion'),
            riego=form.cleaned_data.get('riego'),
            mes_siembra=form.cleaned_data.get('mes_siembra'),
        )
    else:
        cultivos = repo.get_all()

    cultivos_con_imagen = [
        {'cultivo': c, 'imagen_url': _imagen_url(c.nombre)}
        for c in cultivos
    ]

    return render(request, 'huertosmart/cultivos/lista.html', {
        'form': form,
        'cultivos_con_imagen': cultivos_con_imagen,
        'total': cultivos.count(),
    })


def detalle_cultivo(request, cultivo_slug):
    """Ficha detallada de un cultivo usando slug."""
    cultivo = Cultivo.objects.filter(slug=cultivo_slug).first()
    if cultivo is None:
        return redirect('huertosmart:lista_cultivos')

    meses_siembra = [m.strip() for m in cultivo.meses_siembra.split(',') if m.strip()]
    meses_cosecha = [m.strip() for m in cultivo.meses_cosecha.split(',') if m.strip()]

    return render(request, 'huertosmart/cultivos/detalle.html', {
        'cultivo': cultivo,
        'imagen_url': _imagen_url(cultivo.nombre),
        'meses_siembra': meses_siembra,
        'meses_cosecha': meses_cosecha,
        'enfermedades': cultivo.enfermedades.all(),
    })


# F1 - DIAGNÓSTICO POR FOTO

@login_required
def diagnostico_nuevo(request):
    if request.method != 'POST':
        huertos = HuertoRepository().get_huertos_usuario(request.user)
        return render(request, 'huertosmart/diagnostico/nuevo.html', {'huertos': huertos})

    imagen = request.FILES.get('imagen')
    if not imagen:
        messages.error(request, 'Debes seleccionar una imagen.')
        return redirect('huertosmart:diagnostico_nuevo')

    imagen_bytes = imagen.read()

    es_planta = True
    try:
        from .services.aws_service import get_aws_service
        aws = get_aws_service()
        resultado_rekognition = aws.validar_es_planta(imagen_bytes)
        es_planta = resultado_rekognition['es_planta']
        if not es_planta:
            messages.warning(request, resultado_rekognition['mensaje'])
            return redirect('huertosmart:diagnostico_nuevo')
    except Exception as e:
        logger.warning(f"Rekognition no disponible, se omite validación: {e}")

    try:
        from .services.ia_service import get_servicio_ia
        servicio = get_servicio_ia()
        resultado_ia = servicio.diagnosticar(imagen_bytes)
    except Exception as e:
        logger.error(f"Error en modelo IA: {e}")
        messages.error(request, 'El servicio de diagnóstico no está disponible en este momento.')
        return redirect('huertosmart:diagnostico_nuevo')

    nombre_clase = resultado_ia['nombre_clase']
    confianza = resultado_ia['confianza']

    if confianza < UMBRAL_CONFIANZA_MINIMA:
        messages.warning(request, f'La confianza del modelo es muy baja ({confianza}%). Sube una foto más clara.')
        return redirect('huertosmart:diagnostico_nuevo')

    enfermedad = Enfermedad.objects.filter(nombre_modelo=nombre_clase).first()

    siembra_id = request.POST.get('siembra')
    siembra = None
    if siembra_id:
        try:
            siembra = Siembra.objects.get(pk=siembra_id, huerto__usuario=request.user)
        except Siembra.DoesNotExist:
            pass

    imagen.seek(0)
    diagnostico = Diagnostico.objects.create(
        usuario=request.user,
        siembra=siembra,
        imagen=imagen,
        enfermedad_detectada=enfermedad,
        confianza=confianza,
        es_planta_valida=es_planta,
        notas_usuario=request.POST.get('notas', ''),
    )

    return redirect('huertosmart:diagnostico_detalle', diagnostico_id=diagnostico.pk)


@login_required
def diagnostico_detalle(request, diagnostico_id):
    repo = DiagnosticoRepository()
    diagnostico = repo.get_by_id(diagnostico_id)

    if diagnostico is None or diagnostico.usuario != request.user:
        messages.error(request, 'No tienes acceso a ese diagnóstico.')
        return redirect('huertosmart:diagnostico_historial')

    return render(request, 'huertosmart/diagnostico/detalle.html', {
        'diagnostico': diagnostico,
        'confianza_baja': diagnostico.confianza < 70,
    })


@login_required
def diagnostico_historial(request):
    repo = DiagnosticoRepository()
    return render(request, 'huertosmart/diagnostico/historial.html', {
        'diagnosticos': repo.get_diagnosticos_usuario(request.user),
    })


# F4 - MI HUERTO

@login_required
def mi_huerto(request):
    repo = HuertoRepository()
    huertos = repo.get_huertos_usuario(request.user)
    if not huertos.exists():
        messages.info(request, 'Todavía no tienes ningún huerto. ¡Crea el primero!')
        return redirect('huertosmart:crear_huerto')
    return render(request, 'huertosmart/huerto/panel.html', {'huertos': huertos})


@login_required
def crear_huerto(request):
    if request.method == 'POST':
        form = HuertoForm(request.POST)
        if form.is_valid():
            huerto = form.save(commit=False)
            huerto.usuario = request.user
            huerto.save()
            messages.success(request, f'Huerto "{huerto.nombre}" creado correctamente.')
            return redirect('huertosmart:detalle_huerto', huerto_slug=huerto.slug)
    else:
        form = HuertoForm()
    return render(request, 'huertosmart/huerto/crear.html', {'form': form})


@login_required
def detalle_huerto(request, huerto_slug):
    """Detalle de un huerto usando slug.

    LÓGICA DE NEGOCIO: solo el propietario puede ver su huerto.
    """
    siembra_repo = SiembraRepository()

    huerto = Huerto.objects.filter(slug=huerto_slug, activo=True).first()
    if huerto is None or huerto.usuario != request.user:
        messages.error(request, 'No tienes acceso a ese huerto.')
        return redirect('huertosmart:mi_huerto')

    estado_filtro = request.GET.get('estado', '')
    siembras = siembra_repo.filtrar_por_estado(huerto, estado_filtro) if estado_filtro else siembra_repo.get_siembras_huerto(huerto)

    prediccion, alertas = [], []
    if huerto.codigo_postal:
        try:
            from .services.aemet_service import get_alertas_huerto
            resultado = get_alertas_huerto(huerto.codigo_postal)
            prediccion = resultado['prediccion']
            alertas = resultado['alertas']
        except Exception as e:
            logger.warning(f"AEMET no disponible: {e}")

    return render(request, 'huertosmart/huerto/detalle.html', {
        'huerto': huerto,
        'siembras': siembras,
        'estado_filtro': estado_filtro,
        'estados': [('', 'Todas')] + list(Siembra.ESTADO_CHOICES),
        'prediccion': prediccion,
        'alertas': alertas,
    })



@login_required
def eliminar_huerto(request, huerto_slug):
    """Elimina un huerto del usuario previa confirmación.

    LÓGICA DE NEGOCIO: solo el propietario puede eliminar su huerto.
    Solo acepta POST para evitar eliminaciones accidentales por GET.
    """
    huerto = Huerto.objects.filter(slug=huerto_slug, activo=True).first()
    if huerto is None or huerto.usuario != request.user:
        messages.error(request, 'No tienes acceso a ese huerto.')
        return redirect('huertosmart:mi_huerto')

    if request.method == 'POST':
        nombre = huerto.nombre
        huerto.delete()
        messages.success(request, f'El huerto "{nombre}" ha sido eliminado.')
        return redirect('huertosmart:mi_huerto')

    return render(request, 'huertosmart/huerto/confirmar_eliminar.html', {'huerto': huerto})

@login_required
def nueva_siembra(request, huerto_slug):
    """Nueva siembra en un huerto usando slug."""
    huerto = Huerto.objects.filter(slug=huerto_slug, activo=True).first()

    if huerto is None or huerto.usuario != request.user:
        messages.error(request, 'No tienes acceso a ese huerto.')
        return redirect('huertosmart:mi_huerto')

    if request.method == 'POST':
        form = SiembraForm(request.POST)
        if form.is_valid():
            siembra = form.save(commit=False)
            siembra.huerto = huerto
            siembra.save()
            messages.success(request, f'Siembra de {siembra.cultivo.nombre} registrada.')
            return redirect('huertosmart:detalle_huerto', huerto_slug=huerto.slug)
    else:
        form = SiembraForm()

    return render(request, 'huertosmart/huerto/nueva_siembra.html', {'form': form, 'huerto': huerto})


# EXPORTAR A EXCEL

@login_required
def exportar_excel(request):
    siembra_repo = SiembraRepository()
    huerto_repo = HuertoRepository()
    huertos = huerto_repo.get_huertos_usuario(request.user)

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    estilo_cabecera = Font(bold=True, color='FFFFFF')
    fondo_cabecera = PatternFill(fill_type='solid', fgColor='1F6B3A')
    fondo_par = PatternFill(fill_type='solid', fgColor='E8F5E9')
    alineacion_centro = Alignment(horizontal='center')

    columnas = [
        ('Cultivo', 20), ('Fecha siembra', 15), ('Cosecha estimada', 18),
        ('Cosecha real', 15), ('Cantidad (plantas)', 18), ('Estado', 15), ('Notas', 40),
    ]

    for huerto in huertos:
        ws = wb.create_sheet(title=huerto.nombre[:31])
        for col_idx, (nombre_col, ancho) in enumerate(columnas, start=1):
            celda = ws.cell(row=1, column=col_idx, value=nombre_col)
            celda.font = estilo_cabecera
            celda.fill = fondo_cabecera
            celda.alignment = alineacion_centro
            ws.column_dimensions[celda.column_letter].width = ancho

        siembras = siembra_repo.get_siembras_huerto(huerto)
        for fila_idx, siembra in enumerate(siembras, start=2):
            valores = [
                siembra.cultivo.nombre,
                siembra.fecha_siembra.strftime('%d/%m/%Y') if siembra.fecha_siembra else '',
                siembra.fecha_cosecha_estimada.strftime('%d/%m/%Y') if siembra.fecha_cosecha_estimada else '',
                siembra.fecha_cosecha_real.strftime('%d/%m/%Y') if siembra.fecha_cosecha_real else '',
                siembra.cantidad,
                siembra.get_estado_display(),
                siembra.notas,
            ]
            for col_idx, valor in enumerate(valores, start=1):
                celda = ws.cell(row=fila_idx, column=col_idx, value=valor)
                if fila_idx % 2 == 0:
                    celda.fill = fondo_par

        if not siembras.exists():
            ws.cell(row=2, column=1, value='Este huerto no tiene siembras registradas.')

    if not huertos.exists():
        ws = wb.create_sheet(title='Sin datos')
        ws.cell(row=1, column=1, value='No tienes huertos registrados en HuertoSmart.')

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="huertosmart_{request.user.username}.xlsx"'
    return response
