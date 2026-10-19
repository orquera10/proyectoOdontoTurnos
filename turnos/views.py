import calendar
from datetime import date, datetime, time, timedelta
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import (
    BloqueoAgenda,
    ConfiguracionClinica,
    Paciente,
    Tratamiento,
    Turno,
)

ICONOS_MATERIAL_POR_ORDEN = {
    1: "dentistry",
    2: "cleaning_services",
    3: "auto_fix_high",
    4: "grid_view",
    5: "healing",
    6: "vital_signs",
    7: "precision_manufacturing",
    8: "emergency",
}


def asegurar_datos_demo():
    """Inicializa datos de demostración profesionales si la base de datos está vacía."""
    config = ConfiguracionClinica.obtener()

    if not User.objects.filter(username="secretaria").exists():
        sec = User.objects.create_user(
            username="secretaria",
            email="secretaria@dramarianabustamante.com.ar",
            password="belgrano2026",
            first_name="Laura",
            last_name="Secretaría Consultorio",
        )
        sec.is_staff = True
        sec.save()

    if not User.objects.filter(username="mariana").exists():
        dra = User.objects.create_superuser(
            username="mariana",
            email="mariana@dramarianabustamante.com.ar",
            password="odontologia2026",
            first_name="Dra. Mariana",
            last_name="Sánchez de Bustamante",
        )
        dra.save()

    if Tratamiento.objects.count() == 0:
        tratamientos_demo = [
            {
                "nombre": "Consulta General & Diagnóstico 3D",
                "descripcion": "Evaluación clínica integral, odontograma digital HD y plan de tratamiento personalizado con la Dra. Mariana Sánchez de Bustamante.",
                "duracion_minutos": 45,
                "icono": "dentistry",
                "color_tag": "teal",
                "orden": 1,
            },
            {
                "nombre": "Limpieza y Profilaxis Ultrasónica",
                "descripcion": "Eliminación de sarro supragingival por ultrasonido, pulido con pasta fluorada y remoción de manchas.",
                "duracion_minutos": 45,
                "icono": "cleaning_services",
                "color_tag": "cyan",
                "orden": 2,
            },
            {
                "nombre": "Estética & Blanqueamiento LED",
                "descripcion": "Aclaramiento de tono seguro sin sensibilidad dentaria y diseño de sonrisa con carillas estéticas.",
                "duracion_minutos": 60,
                "icono": "auto_fix_high",
                "color_tag": "indigo",
                "orden": 3,
            },
            {
                "nombre": "Ortodoncia & Alineadores Invisibles",
                "descripcion": "Control de ortodoncia fija estética y planificación 3D con alineadores transparentes.",
                "duracion_minutos": 45,
                "icono": "grid_view",
                "color_tag": "violet",
                "orden": 4,
            },
            {
                "nombre": "Operatoria y Restauraciones Estéticas",
                "descripcion": "Restauraciones con resinas fotopolimerizables de alta estética que imitan el tono natural de tu pieza.",
                "duracion_minutos": 45,
                "icono": "healing",
                "color_tag": "emerald",
                "orden": 5,
            },
            {
                "nombre": "Endodoncia (Tratamiento de Conducto)",
                "descripcion": "Tratamiento mecanizado sin dolor para conservar piezas dentales con afección pulpar.",
                "duracion_minutos": 60,
                "icono": "vital_signs",
                "color_tag": "amber",
                "orden": 6,
            },
            {
                "nombre": "Implantes & Rehabilitación Protésica",
                "descripcion": "Reemplazo biocompatible de piezas faltantes con implantes de titanio y coronas libres de metal.",
                "duracion_minutos": 60,
                "icono": "precision_manufacturing",
                "color_tag": "blue",
                "orden": 7,
            },
            {
                "nombre": "Dolor Agudo / Urgencia Dental",
                "descripcion": "Atención prioritaria en el día para dolor dental agudo, fracturas, inflamación o caída de provisorios.",
                "duracion_minutos": 30,
                "icono": "emergency",
                "color_tag": "rose",
                "orden": 8,
            },
        ]
        for item in tratamientos_demo:
            Tratamiento.objects.create(**item)
    else:
        # Asegurar que los íconos de Material Symbols estén actualizados
        for trat in Tratamiento.objects.all():
            if trat.icono not in ICONOS_MATERIAL_POR_ORDEN.values():
                trat.icono = ICONOS_MATERIAL_POR_ORDEN.get(trat.orden, "dentistry")
                trat.save(update_fields=["icono"])

    if Turno.objects.count() == 0:
        hoy = timezone.localdate()
        fecha_base = hoy if hoy.weekday() != 6 else hoy + timedelta(days=1)
        manana = fecha_base + timedelta(days=1)
        if manana.weekday() == 6:
            manana += timedelta(days=1)

        tratamientos = list(Tratamiento.objects.all())
        pacientes_data = [
            {
                "nombre_completo": "Valentina Gómez Alvear",
                "dni": "38492104",
                "telefono": "11 5823-9941",
                "email": "valen.gomez@email.com",
                "obra_social": "OSDE",
                "numero_afiliado": "61-0492817-02",
                "observaciones_medicas": "Sin alergias conocidas. Control semestral.",
            },
            {
                "nombre_completo": "Martín Ignacio Pellegrini",
                "dni": "32910485",
                "telefono": "11 4912-3380",
                "email": "mpellegrini@email.com",
                "obra_social": "Swiss Medical",
                "numero_afiliado": "800419283",
                "observaciones_medicas": "Sensibilidad en molar inferior derecho (pieza 46).",
            },
            {
                "nombre_completo": "Lucía Fernández Madero",
                "dni": "41203948",
                "telefono": "11 6204-1175",
                "email": "lucia.fmadero@email.com",
                "obra_social": "Particular",
                "numero_afiliado": "",
                "observaciones_medicas": "Interesada en blanqueamiento LED y alineadores.",
            },
            {
                "nombre_completo": "Santiago Rodríguez Peña",
                "dni": "29847162",
                "telefono": "11 3490-8271",
                "email": "santi.rpena@email.com",
                "obra_social": "Galeno",
                "numero_afiliado": "4502918-1",
                "observaciones_medicas": "Alergia a penicilina. En tratamiento de conducto.",
            },
            {
                "nombre_completo": "Camila Etcheverry",
                "dni": "43918274",
                "telefono": "11 5109-4420",
                "email": "cami.etcheverry@email.com",
                "obra_social": "Medifé",
                "numero_afiliado": "99201844",
                "observaciones_medicas": "Control mensual de ortodoncia.",
            },
            {
                "nombre_completo": "Roberto Carlos Mendizábal",
                "dni": "24109384",
                "telefono": "11 4029-6712",
                "email": "rmendizabal@email.com",
                "obra_social": "Omint",
                "numero_afiliado": "33019284",
                "observaciones_medicas": "Prueba de corona de porcelana.",
            },
            {
                "nombre_completo": "Sofía Aramburu",
                "dni": "39102938",
                "telefono": "11 6781-2093",
                "email": "sofia.aramburu@email.com",
                "obra_social": "OSDE",
                "numero_afiliado": "62-9918273-01",
                "observaciones_medicas": "Primera consulta diagnóstica.",
            },
        ]

        pacientes_objs = []
        for p in pacientes_data:
            pac, _ = Paciente.objects.get_or_create(dni=p["dni"], defaults=p)
            pacientes_objs.append(pac)

        turnos_iniciales = [
            {
                "paciente": pacientes_objs[0],
                "tratamiento": tratamientos[1],
                "fecha": fecha_base,
                "hora": time(9, 0),
                "estado": Turno.ESTADO_ATENDIDO,
                "origen": Turno.ORIGEN_WEB,
                "motivo_notas": "Limpieza semestral y control de encías.",
                "notas_secretaria": "Atendido por Dra. Mariana Sánchez de Bustamante. Próximo control en 6 meses.",
            },
            {
                "paciente": pacientes_objs[1],
                "tratamiento": tratamientos[4],
                "fecha": fecha_base,
                "hora": time(9, 30),
                "estado": Turno.ESTADO_EN_SALA,
                "origen": Turno.ORIGEN_SECRETARIA,
                "motivo_notas": "Molestia al tomar cosas frías en muela inferior.",
                "notas_secretaria": "Paciente ya en sala de espera. Trajo radiografía panorámica.",
            },
            {
                "paciente": pacientes_objs[2],
                "tratamiento": tratamientos[2],
                "fecha": fecha_base,
                "hora": time(10, 30),
                "estado": Turno.ESTADO_CONFIRMADO,
                "origen": Turno.ORIGEN_WEB,
                "motivo_notas": "Consulta por blanqueamiento dental LED.",
                "notas_secretaria": "Confirmado por WhatsApp ayer a las 18hs.",
            },
            {
                "paciente": pacientes_objs[3],
                "tratamiento": tratamientos[5],
                "fecha": fecha_base,
                "hora": time(11, 30),
                "estado": Turno.ESTADO_CONFIRMADO,
                "origen": Turno.ORIGEN_SECRETARIA,
                "motivo_notas": "Segunda sesión de conducto.",
                "notas_secretaria": "Importante: paciente alérgico a penicilina.",
            },
            {
                "paciente": pacientes_objs[4],
                "tratamiento": tratamientos[3],
                "fecha": fecha_base,
                "hora": time(15, 30),
                "estado": Turno.ESTADO_PENDIENTE,
                "origen": Turno.ORIGEN_WEB,
                "motivo_notas": "Ajuste de alineadores invisibles.",
                "notas_secretaria": "Pendiente validación telefónica / WhatsApp.",
            },
            {
                "paciente": pacientes_objs[6],
                "tratamiento": tratamientos[0],
                "fecha": fecha_base,
                "hora": time(16, 30),
                "estado": Turno.ESTADO_PENDIENTE,
                "origen": Turno.ORIGEN_WEB,
                "motivo_notas": "Primera vez con la Dra. Mariana Sánchez de Bustamante.",
                "notas_secretaria": "Reservó desde el portal web de pacientes.",
            },
            {
                "paciente": pacientes_objs[5],
                "tratamiento": tratamientos[6],
                "fecha": manana,
                "hora": time(10, 0),
                "estado": Turno.ESTADO_CONFIRMADO,
                "origen": Turno.ORIGEN_SECRETARIA,
                "motivo_notas": "Colocación de corona definitiva.",
                "notas_secretaria": "El laboratorio ya entregó la pieza.",
            },
        ]

        for t_data in turnos_iniciales:
            Turno.objects.create(**t_data)

    return config


def obtener_fecha_default_agenda():
    hoy = timezone.localdate()
    if hoy.weekday() == 6:
        return hoy + timedelta(days=1)
    return hoy


NOMBRES_DIA_COMPLETO = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
NOMBRES_MES_COMPLETO = [
    "",
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]


def formatear_fecha_es(fecha_obj):
    return f"{NOMBRES_DIA_COMPLETO[fecha_obj.weekday()]}, {fecha_obj.day} de {NOMBRES_MES_COMPLETO[fecha_obj.month]} {fecha_obj.year}"


def calcular_disponibilidad_fecha(fecha_obj):
    """Devuelve el detalle de todos los horarios de una fecha y si están disponibles o tomados."""
    horarios_posibles = Turno.horarios_del_dia(fecha_obj)
    bloqueo_dia = BloqueoAgenda.objects.filter(fecha=fecha_obj, todo_el_dia=True).first()
    if bloqueo_dia:
        return {
            "bloqueado_completo": True,
            "motivo_bloqueo": bloqueo_dia.motivo,
            "es_domingo": False,
            "slots": [],
            "libres_count": 0,
        }

    if fecha_obj.weekday() == 6:
        return {
            "bloqueado_completo": False,
            "motivo_bloqueo": "El consultorio permanece cerrado los días domingo.",
            "es_domingo": True,
            "slots": [],
            "libres_count": 0,
        }

    turnos_activos = (
        Turno.objects.filter(fecha=fecha_obj)
        .exclude(estado=Turno.ESTADO_CANCELADO)
        .select_related("paciente", "tratamiento")
    )

    ocupados_por_hora = {}
    for t in turnos_activos:
        hora_str = t.hora.strftime("%H:%M")
        ocupados_por_hora.setdefault(hora_str, []).append(t)

    hoy = timezone.localdate()
    ahora_time = timezone.localtime().time()

    slots = []
    libres_count = 0
    for h in horarios_posibles:
        hora_str = h.strftime("%H:%M")
        turnos_en_hora = ocupados_por_hora.get(hora_str, [])
        ya_paso = (fecha_obj < hoy) or (fecha_obj == hoy and h <= ahora_time)
        ocupado = len(turnos_en_hora) > 0
        disponible_web = (not ocupado) and (not ya_paso)
        if disponible_web:
            libres_count += 1

        slots.append(
            {
                "hora": hora_str,
                "franja": "Mañana" if h.hour < 14 else "Tarde",
                "disponible": disponible_web,
                "ocupado": ocupado,
                "ya_paso": ya_paso,
                "cantidad_turnos": len(turnos_en_hora),
                "turnos": turnos_en_hora,
            }
        )

    return {
        "bloqueado_completo": False,
        "motivo_bloqueo": "",
        "es_domingo": False,
        "slots": slots,
        "libres_count": libres_count,
    }


def landing_cliente(request):
    """Portal Pacientes — Reserva Minimalista y Amigable para la Dra. Mariana Sánchez de Bustamante."""
    config = asegurar_datos_demo()
    tratamientos = Tratamiento.objects.filter(activo=True)
    hoy = timezone.localdate()
    fecha_sugerida = obtener_fecha_default_agenda()

    # Días hábiles próximos en tarjetas grandes y legibles (imposible equivocarse de día)
    dias_amigables = []
    cursor = fecha_sugerida
    while len(dias_amigables) < 8:
        if cursor.weekday() != 6:  # Excluir domingos
            if cursor == hoy:
                etiqueta_arriba = "HOY"
            elif cursor == hoy + timedelta(days=1):
                etiqueta_arriba = "MAÑANA"
            else:
                etiqueta_arriba = NOMBRES_DIA_COMPLETO[cursor.weekday()][:3].upper()

            dias_amigables.append(
                {
                    "fecha_iso": cursor.isoformat(),
                    "etiqueta_arriba": etiqueta_arriba,
                    "nombre_dia": NOMBRES_DIA_COMPLETO[cursor.weekday()],
                    "dia_numero": cursor.day,
                    "mes_corto": NOMBRES_MES_COMPLETO[cursor.month][:3],
                    "fecha_larga": f"{NOMBRES_DIA_COMPLETO[cursor.weekday()]} {cursor.day} de {NOMBRES_MES_COMPLETO[cursor.month]}",
                    "es_seleccionado": cursor == fecha_sugerida,
                }
            )
        cursor += timedelta(days=1)

    context = {
        "config": config,
        "tratamientos": tratamientos,
        "primer_tratamiento": tratamientos.first(),
        "obras_sociales": Paciente.OBRAS_SOCIALES,
        "fecha_sugerida": fecha_sugerida.isoformat(),
        "fecha_sugerida_larga": f"{NOMBRES_DIA_COMPLETO[fecha_sugerida.weekday()]} {fecha_sugerida.day} de {NOMBRES_MES_COMPLETO[fecha_sugerida.month]}",
        "fecha_minima": hoy.isoformat(),
        "dias_amigables": dias_amigables,
    }
    return render(request, "turnos/landing.html", context)


@require_GET
def api_horarios_disponibles(request):
    """Endpoint JSON que devuelve horarios disponibles en tiempo real para una fecha dada."""
    asegurar_datos_demo()
    fecha_str = request.GET.get("fecha", "")
    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        fecha_obj = obtener_fecha_default_agenda()

    info = calcular_disponibilidad_fecha(fecha_obj)
    slots_serializados = [
        {
            "hora": s["hora"],
            "franja": s["franja"],
            "disponible": s["disponible"],
            "ocupado": s["ocupado"],
            "ya_paso": s["ya_paso"],
            "paciente_actual": (
                s["turnos"][0].paciente.nombre_completo
                if (request.user.is_authenticated and s["turnos"])
                else ""
            ),
        }
        for s in info["slots"]
    ]

    return JsonResponse(
        {
            "fecha": fecha_obj.isoformat(),
            "fecha_formateada": fecha_obj.strftime("%d/%m/%Y"),
            "fecha_larga": f"{NOMBRES_DIA_COMPLETO[fecha_obj.weekday()]} {fecha_obj.day} de {NOMBRES_MES_COMPLETO[fecha_obj.month]}",
            "es_domingo": info["es_domingo"],
            "bloqueado_completo": info["bloqueado_completo"],
            "motivo_bloqueo": info["motivo_bloqueo"],
            "libres_count": info["libres_count"],
            "slots": slots_serializados,
        }
    )


@require_POST
def reservar_turno_cliente(request):
    """Procesa la solicitud de reserva de turno desde el Portal de Pacientes."""
    config = asegurar_datos_demo()

    nombre_completo = request.POST.get("nombre_completo", "").strip()
    dni = "".join(ch for ch in request.POST.get("dni", "") if ch.isdigit())
    telefono = request.POST.get("telefono", "").strip()
    email = request.POST.get("email", "").strip()
    obra_social = request.POST.get("obra_social", "Particular").strip()
    numero_afiliado = request.POST.get("numero_afiliado", "").strip()
    tratamiento_id = request.POST.get("tratamiento_id", "")
    fecha_str = request.POST.get("fecha", "")
    hora_str = request.POST.get("hora", "")
    motivo_notas = request.POST.get("motivo_notas", "").strip()

    if not all([nombre_completo, dni, telefono, tratamiento_id, fecha_str, hora_str]):
        messages.error(
            request,
            "Por favor completá todos los campos obligatorios (Tratamiento, Fecha, Horario, Nombre, DNI y Teléfono).",
        )
        return redirect("/#reservar-turno")

    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora_obj = datetime.strptime(hora_str, "%H:%M").time()
        tratamiento = Tratamiento.objects.get(pk=tratamiento_id, activo=True)
    except (ValueError, Tratamiento.DoesNotExist):
        messages.error(request, "Los datos de fecha, horario o tratamiento no son válidos.")
        return redirect("/#reservar-turno")

    if fecha_obj < timezone.localdate():
        messages.error(request, "No es posible agendar turnos en fechas pasadas.")
        return redirect("/#reservar-turno")

    if fecha_obj.weekday() == 6:
        messages.error(request, "El consultorio permanece cerrado los días domingo.")
        return redirect("/#reservar-turno")

    ya_ocupado = (
        Turno.objects.filter(fecha=fecha_obj, hora=hora_obj)
        .exclude(estado=Turno.ESTADO_CANCELADO)
        .exists()
    )
    if ya_ocupado:
        messages.error(
            request,
            f"El horario {hora_str} hs del {fecha_obj:%d/%m/%Y} acaba de ser reservado. Por favor elegí otro horario disponible.",
        )
        return redirect("/#reservar-turno")

    paciente, creado = Paciente.objects.get_or_create(
        dni=dni,
        defaults={
            "nombre_completo": nombre_completo,
            "telefono": telefono,
            "email": email,
            "obra_social": obra_social,
            "numero_afiliado": numero_afiliado,
        },
    )
    if not creado:
        paciente.nombre_completo = nombre_completo
        paciente.telefono = telefono
        if email:
            paciente.email = email
        paciente.obra_social = obra_social
        if numero_afiliado:
            paciente.numero_afiliado = numero_afiliado
        paciente.save()

    nuevo_turno = Turno.objects.create(
        paciente=paciente,
        tratamiento=tratamiento,
        fecha=fecha_obj,
        hora=hora_obj,
        estado=Turno.ESTADO_PENDIENTE,
        origen=Turno.ORIGEN_WEB,
        motivo_notas=motivo_notas,
    )

    return redirect("comprobante_turno", codigo=nuevo_turno.codigo)


def comprobante_turno(request, codigo):
    """Muestra el comprobante digital del turno agendado con opción de enviar por WhatsApp o imprimir."""
    config = asegurar_datos_demo()
    turno = get_object_or_404(
        Turno.objects.select_related("paciente", "tratamiento"),
        codigo=codigo.upper().strip(),
    )

    mensaje_wa = (
        f"Hola! Solicité un turno web con la {config.odontologa_titular}.\n"
        f"• Código de turno: *{turno.codigo}*\n"
        f"• Paciente: {turno.paciente.nombre_completo} (DNI {turno.paciente.dni})\n"
        f"• Fecha: {turno.fecha:%d/%m/%Y} a las {turno.hora:%H:%M} hs\n"
        f"• Tratamiento: {turno.tratamiento.nombre}\n"
        f"• Cobertura: {turno.paciente.obra_social}"
    )
    url_whatsapp_clinica = f"https://wa.me/{config.whatsapp_numero}?text={quote(mensaje_wa)}"

    return render(
        request,
        "turnos/comprobante.html",
        {
            "config": config,
            "turno": turno,
            "url_whatsapp_clinica": url_whatsapp_clinica,
        },
    )


@require_POST
def cancelar_turno_paciente(request, codigo):
    """Permite al paciente cancelar su propio turno desde el comprobante."""
    turno = get_object_or_404(Turno, codigo=codigo.upper().strip())
    dni_confirmacion = "".join(ch for ch in request.POST.get("dni", "") if ch.isdigit())
    if dni_confirmacion != turno.paciente.dni:
        messages.error(request, "El DNI ingresado no coincide con el titular del turno.")
        return redirect("comprobante_turno", codigo=turno.codigo)

    turno.estado = Turno.ESTADO_CANCELADO
    turno.notas_secretaria = (
        f"{turno.notas_secretaria}\n[Cancelado por el paciente desde la web el {timezone.localtime():%d/%m/%Y %H:%M}]".strip()
    )
    turno.save()
    messages.success(request, f"El turno {turno.codigo} ha sido cancelado correctamente. El horario quedó liberado.")
    return redirect("comprobante_turno", codigo=turno.codigo)


@require_GET
def api_consultar_turno(request):
    """Permite a un paciente buscar sus turnos vigentes por DNI o código de reserva MSB-XXXX."""
    asegurar_datos_demo()
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"encontrado": False, "mensaje": "Ingresá tu DNI o código de turno."})

    solo_digitos = "".join(ch for ch in q if ch.isdigit())
    hoy = timezone.localdate()

    if q.upper().startswith("MSB-"):
        turnos = Turno.objects.filter(codigo__iexact=q).select_related("paciente", "tratamiento")
    elif solo_digitos:
        turnos = (
            Turno.objects.filter(paciente__dni=solo_digitos, fecha__gte=hoy)
            .exclude(estado=Turno.ESTADO_CANCELADO)
            .select_related("paciente", "tratamiento")
            .order_by("fecha", "hora")
        )
    else:
        turnos = Turno.objects.none()

    resultados = []
    for t in turnos[:5]:
        resultados.append(
            {
                "codigo": t.codigo,
                "paciente": t.paciente.nombre_completo,
                "tratamiento": t.tratamiento.nombre,
                "fecha": t.fecha.strftime("%d/%m/%Y"),
                "hora": t.hora.strftime("%H:%M"),
                "estado_display": t.get_estado_display(),
                "estado": t.estado,
                "url_comprobante": f"/turno/{t.codigo}/",
            }
        )

    if not resultados:
        return JsonResponse(
            {
                "encontrado": False,
                "mensaje": "No encontramos turnos próximos activos con ese DNI o código.",
            }
        )

    return JsonResponse({"encontrado": True, "turnos": resultados})


# ==============================================================================
# VISTAS DEL DASHBOARD DE SECRETARÍA Y DRA. MARIANA SÁNCHEZ DE BUSTAMANTE
# ==============================================================================


def login_secretaria(request):
    """Acceso al panel de gestión de secretaría y consultorio."""
    config = asegurar_datos_demo()
    if request.user.is_authenticated:
        return redirect("dashboard_secretaria")

    if request.method == "POST":
        acceso_rapido = request.POST.get("acceso_rapido", "")
        if acceso_rapido == "secretaria":
            user = User.objects.filter(username="secretaria").first()
            if user:
                login(request, user)
                messages.success(request, "Bienvenida Laura (Secretaría) al panel de gestión clínica.")
                return redirect("dashboard_secretaria")
        elif acceso_rapido == "doctora":
            user = User.objects.filter(username="mariana").first()
            if user:
                login(request, user)
                messages.success(request, "Bienvenida Dra. Mariana Sánchez de Bustamante.")
                return redirect("dashboard_secretaria")

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenida/o {user.first_name or user.username} al sistema de gestión.")
            return redirect("dashboard_secretaria")
        else:
            messages.error(request, "Usuario o contraseña incorrectos. Podés usar el botón de Acceso Demo con 1 clic.")

    return render(request, "turnos/login_secretaria.html", {"config": config})


def logout_secretaria(request):
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("login_secretaria")


@login_required
def dashboard_secretaria(request):
    """Dashboard principal para la secretaria y la Dra. Mariana Sánchez de Bustamante."""
    config = asegurar_datos_demo()
    hoy = timezone.localdate()

    fecha_param = request.GET.get("fecha", "")
    vista_modo = request.GET.get("vista", "dia")  # 'dia' o 'todos'
    estado_filtro = request.GET.get("estado", "TODOS")
    busqueda = request.GET.get("q", "").strip()

    try:
        fecha_seleccionada = datetime.strptime(fecha_param, "%Y-%m-%d").date()
    except ValueError:
        fecha_seleccionada = obtener_fecha_default_agenda()

    fecha_anterior = fecha_seleccionada - timedelta(days=1)
    if fecha_anterior.weekday() == 6:
        fecha_anterior -= timedelta(days=1)
    fecha_siguiente = fecha_seleccionada + timedelta(days=1)
    if fecha_siguiente.weekday() == 6:
        fecha_siguiente += timedelta(days=1)

    turnos_del_dia_qs = Turno.objects.filter(fecha=fecha_seleccionada).select_related(
        "paciente", "tratamiento"
    )

    total_dia = turnos_del_dia_qs.exclude(estado=Turno.ESTADO_CANCELADO).count()
    confirmados_dia = turnos_del_dia_qs.filter(estado=Turno.ESTADO_CONFIRMADO).count()
    pendientes_dia = turnos_del_dia_qs.filter(estado=Turno.ESTADO_PENDIENTE).count()
    en_sala_dia = turnos_del_dia_qs.filter(estado=Turno.ESTADO_EN_SALA).count()
    atendidos_dia = turnos_del_dia_qs.filter(estado=Turno.ESTADO_ATENDIDO).count()
    cancelados_dia = turnos_del_dia_qs.filter(estado=Turno.ESTADO_CANCELADO).count()
    sobreturnos_dia = turnos_del_dia_qs.filter(es_sobreturno=True).exclude(estado=Turno.ESTADO_CANCELADO).count()
    web_pendientes_total = Turno.objects.filter(estado=Turno.ESTADO_PENDIENTE, fecha__gte=hoy).count()

    disponibilidad_dia = calcular_disponibilidad_fecha(fecha_seleccionada)

    kpis_dia = {
        "total": total_dia,
        "confirmados": confirmados_dia,
        "pendientes": pendientes_dia,
        "en_sala": en_sala_dia,
        "atendidos": atendidos_dia,
        "cancelados": cancelados_dia,
        "sobreturnos": sobreturnos_dia,
        "web_pendientes": web_pendientes_total,
        "libres": disponibilidad_dia["libres_count"],
        "listos_y_atendidos": confirmados_dia + atendidos_dia,
    }

    if vista_modo == "todos":
        turnos_listado = Turno.objects.filter(fecha__gte=hoy).select_related(
            "paciente", "tratamiento"
        )
    else:
        turnos_listado = turnos_del_dia_qs

    if estado_filtro != "TODOS":
        turnos_listado = turnos_listado.filter(estado=estado_filtro)

    if busqueda:
        turnos_listado = turnos_listado.filter(
            Q(paciente__nombre_completo__icontains=busqueda)
            | Q(paciente__dni__icontains=busqueda)
            | Q(paciente__telefono__icontains=busqueda)
            | Q(codigo__icontains=busqueda)
            | Q(tratamiento__nombre__icontains=busqueda)
        )

    turnos_enriquecidos = []
    for t in turnos_listado:
        msg_recordatorio = (
            f"Hola {t.paciente.nombre_completo}! Te escribimos del consultorio odontológico de la "
            f"{config.odontologa_titular} ({config.direccion}) para confirmar tu turno del día "
            f"*{t.fecha:%d/%m/%Y} a las {t.hora:%H:%M} hs* ({t.tratamiento.nombre}). "
            f"¿Nos confirmás tu asistencia? ¡Muchas gracias!"
        )
        t.whatsapp_recordatorio_url = (
            f"https://wa.me/{t.paciente.telefono_whatsapp}?text={quote(msg_recordatorio)}"
            if t.paciente.telefono_whatsapp
            else ""
        )
        partes_nombre = t.paciente.nombre_completo.split()
        t.iniciales = "".join(p[0].upper() for p in partes_nombre[:2]) if partes_nombre else "PA"
        # Categoría para el filtro JS instantáneo en la tabla
        if t.estado == Turno.ESTADO_PENDIENTE:
            t.chip_category = "web"
        elif t.estado == Turno.ESTADO_EN_SALA:
            t.chip_category = "espera"
        elif t.estado == Turno.ESTADO_CONFIRMADO:
            t.chip_category = "confirmados"
        elif t.estado == Turno.ESTADO_ATENDIDO:
            t.chip_category = "finalizados"
        elif t.estado == Turno.ESTADO_CANCELADO:
            t.chip_category = "cancelados"
        else:
            t.chip_category = "all"
        turnos_enriquecidos.append(t)

    turnos_en_sala_list = [t for t in turnos_enriquecidos if t.estado == Turno.ESTADO_EN_SALA]
    turnos_web_pendientes_list = (
        Turno.objects.filter(estado=Turno.ESTADO_PENDIENTE, fecha__gte=hoy)
        .select_related("paciente", "tratamiento")
        .order_by("fecha", "hora")[:4]
    )

    tratamientos = Tratamiento.objects.filter(activo=True)
    horarios_todos = [h.strftime("%H:%M") for h in Turno.HORARIOS_BASE]
    slots_libres_sugeridos = [s["hora"] for s in disponibilidad_dia["slots"] if s["disponible"]][:8]
    if not slots_libres_sugeridos:
        slots_libres_sugeridos = ["09:30", "11:00", "15:30", "17:00"]

    context = {
        "config": config,
        "hoy_iso": hoy.isoformat(),
        "fecha_seleccionada": fecha_seleccionada,
        "fecha_seleccionada_iso": fecha_seleccionada.isoformat(),
        "fecha_formateada_es": formatear_fecha_es(fecha_seleccionada),
        "nombre_dia_seleccionado": NOMBRES_DIA_COMPLETO[fecha_seleccionada.weekday()],
        "fecha_anterior_iso": fecha_anterior.isoformat(),
        "fecha_siguiente_iso": fecha_siguiente.isoformat(),
        "vista_modo": vista_modo,
        "estado_filtro": estado_filtro,
        "busqueda": busqueda,
        "kpis": kpis_dia,
        "disponibilidad_dia": disponibilidad_dia,
        "turnos": turnos_enriquecidos,
        "turnos_en_sala_list": turnos_en_sala_list,
        "turnos_web_pendientes_list": turnos_web_pendientes_list,
        "slots_libres_sugeridos": slots_libres_sugeridos,
        "tratamientos": tratamientos,
        "obras_sociales": Paciente.OBRAS_SOCIALES,
        "estados_choices": Turno.ESTADOS_CHOICES,
        "origenes_choices": Turno.ORIGEN_CHOICES,
        "horarios_todos": horarios_todos,
        "total_pacientes_registrados": Paciente.objects.count(),
    }
    return render(request, "turnos/dashboard_secretaria.html", context)


@login_required
@require_POST
def crear_turno_secretaria(request):
    """Permite a la secretaria cargar un nuevo turno o sobreturno desde el Slide-Over Drawer."""
    nombre_completo = request.POST.get("nombre_completo", "").strip()
    dni = "".join(ch for ch in request.POST.get("dni", "") if ch.isdigit())
    telefono = request.POST.get("telefono", "").strip()
    email = request.POST.get("email", "").strip()
    obra_social = request.POST.get("obra_social", "Particular").strip()
    numero_afiliado = request.POST.get("numero_afiliado", "").strip()
    observaciones_medicas = request.POST.get("observaciones_medicas", "").strip()

    tratamiento_id = request.POST.get("tratamiento_id", "")
    fecha_str = request.POST.get("fecha", "")
    hora_str = request.POST.get("hora", "")
    estado = request.POST.get("estado", Turno.ESTADO_CONFIRMADO)
    origen = request.POST.get("origen", Turno.ORIGEN_SECRETARIA)
    es_sobreturno = request.POST.get("es_sobreturno") == "on"
    motivo_notas = request.POST.get("motivo_notas", "").strip()
    notas_secretaria = request.POST.get("notas_secretaria", "").strip()

    if not all([nombre_completo, dni, telefono, tratamiento_id, fecha_str, hora_str]):
        messages.error(request, "Completá Nombre, DNI, Teléfono, Tratamiento, Fecha y Hora para cargar el turno.")
        return redirect(f"/secretaria/?fecha={fecha_str}")

    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora_obj = datetime.strptime(hora_str, "%H:%M").time()
        tratamiento = Tratamiento.objects.get(pk=tratamiento_id)
    except (ValueError, Tratamiento.DoesNotExist):
        messages.error(request, "Fecha, horario o tratamiento inválido.")
        return redirect("dashboard_secretaria")

    ocupado = (
        Turno.objects.filter(fecha=fecha_obj, hora=hora_obj)
        .exclude(estado=Turno.ESTADO_CANCELADO)
        .exists()
    )
    if ocupado and not es_sobreturno:
        messages.warning(
            request,
            f"El horario {hora_str} del {fecha_obj:%d/%m/%Y} ya tiene un paciente asignado. Si querés agregarlo igual, marcá la casilla 'Permitir Sobreturno'.",
        )
        return redirect(f"/secretaria/?fecha={fecha_str}")

    paciente, creado = Paciente.objects.get_or_create(
        dni=dni,
        defaults={
            "nombre_completo": nombre_completo,
            "telefono": telefono,
            "email": email,
            "obra_social": obra_social,
            "numero_afiliado": numero_afiliado,
            "observaciones_medicas": observaciones_medicas,
        },
    )
    if not creado:
        paciente.nombre_completo = nombre_completo
        paciente.telefono = telefono
        if email:
            paciente.email = email
        paciente.obra_social = obra_social
        if numero_afiliado:
            paciente.numero_afiliado = numero_afiliado
        if observaciones_medicas:
            paciente.observaciones_medicas = observaciones_medicas
        paciente.save()

    turno = Turno.objects.create(
        paciente=paciente,
        tratamiento=tratamiento,
        fecha=fecha_obj,
        hora=hora_obj,
        estado=estado,
        origen=origen,
        es_sobreturno=es_sobreturno or ocupado,
        motivo_notas=motivo_notas,
        notas_secretaria=notas_secretaria,
    )

    etiqueta_sobre = " (Sobreturno)" if turno.es_sobreturno else ""
    messages.success(
        request,
        f"Turno {turno.codigo}{etiqueta_sobre} registrado en base de datos para {paciente.nombre_completo} ({fecha_obj:%d/%m/%Y} {hora_str} hs).",
    )
    return redirect(f"/secretaria/?fecha={fecha_str}")


@login_required
@require_POST
def cambiar_estado_turno(request, turno_id):
    """Actualiza el estado de un turno con 1 clic desde el dashboard de la secretaria."""
    turno = get_object_or_404(Turno, pk=turno_id)
    nuevo_estado = request.POST.get("estado", "")
    estados_validos = dict(Turno.ESTADOS_CHOICES).keys()

    if nuevo_estado in estados_validos:
        turno.estado = nuevo_estado
        turno.save(update_fields=["estado", "actualizado_en"])
        messages.success(
            request,
            f"Turno {turno.codigo} ({turno.paciente.nombre_completo}) actualizado a: {turno.get_estado_display()}.",
        )

    next_url = request.POST.get("next") or f"/secretaria/?fecha={turno.fecha.isoformat()}"
    return redirect(next_url)


@login_required
@require_POST
def editar_turno_secretaria(request, turno_id):
    """Permite a la secretaria reprogramar fecha/hora, cambiar tratamiento o guardar notas internas."""
    turno = get_object_or_404(Turno, pk=turno_id)

    fecha_str = request.POST.get("fecha", "")
    hora_str = request.POST.get("hora", "")
    tratamiento_id = request.POST.get("tratamiento_id", "")
    estado = request.POST.get("estado", turno.estado)
    notas_secretaria = request.POST.get("notas_secretaria", "").strip()
    motivo_notas = request.POST.get("motivo_notas", "").strip()
    telefono_paciente = request.POST.get("telefono_paciente", "").strip()
    obra_social_paciente = request.POST.get("obra_social_paciente", "").strip()

    try:
        if fecha_str:
            turno.fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        if hora_str:
            turno.hora = datetime.strptime(hora_str, "%H:%M").time()
        if tratamiento_id:
            turno.tratamiento = Tratamiento.objects.get(pk=tratamiento_id)
    except (ValueError, Tratamiento.DoesNotExist):
        messages.error(request, "Error al actualizar la fecha, hora o tratamiento del turno.")
        return redirect(f"/secretaria/?fecha={turno.fecha.isoformat()}")

    if estado in dict(Turno.ESTADOS_CHOICES):
        turno.estado = estado
    turno.notas_secretaria = notas_secretaria
    turno.motivo_notas = motivo_notas
    turno.save()

    if telefono_paciente or obra_social_paciente:
        pac = turno.paciente
        if telefono_paciente:
            pac.telefono = telefono_paciente
        if obra_social_paciente:
            pac.obra_social = obra_social_paciente
        pac.save()

    messages.success(
        request,
        f"Cambios guardados en el turno {turno.codigo} de {turno.paciente.nombre_completo}.",
    )
    return redirect(f"/secretaria/?fecha={turno.fecha.isoformat()}")


@login_required
@require_GET
def api_buscar_paciente_dni(request):
    """Autocompleta los datos del paciente cuando la secretaria escribe el DNI en el drawer."""
    dni = "".join(ch for ch in request.GET.get("dni", "") if ch.isdigit())
    if not dni:
        return JsonResponse({"encontrado": False})

    paciente = Paciente.objects.filter(dni=dni).first()
    if not paciente:
        return JsonResponse({"encontrado": False})

    ultimo_turno = paciente.turnos.order_by("-fecha", "-hora").first()
    return JsonResponse(
        {
            "encontrado": True,
            "nombre_completo": paciente.nombre_completo,
            "dni": paciente.dni,
            "telefono": paciente.telefono,
            "email": paciente.email,
            "obra_social": paciente.obra_social,
            "numero_afiliado": paciente.numero_afiliado,
            "observaciones_medicas": paciente.observaciones_medicas,
            "ultimo_turno": (
                f"{ultimo_turno.fecha:%d/%m/%Y} - {ultimo_turno.tratamiento.nombre}"
                if ultimo_turno
                else "Paciente regular"
            ),
        }
    )


@login_required
def pacientes_secretaria(request):
    """Padrón de pacientes e historial clínico-administrativo para la secretaria y la Dra. Mariana."""
    config = asegurar_datos_demo()
    busqueda = request.GET.get("q", "").strip()
    obra_filtro = request.GET.get("obra_social", "")

    pacientes_qs = Paciente.objects.annotate(total_turnos=Count("turnos")).order_by(
        "nombre_completo"
    )
    if busqueda:
        pacientes_qs = pacientes_qs.filter(
            Q(nombre_completo__icontains=busqueda)
            | Q(dni__icontains=busqueda)
            | Q(telefono__icontains=busqueda)
            | Q(email__icontains=busqueda)
        )
    if obra_filtro:
        pacientes_qs = pacientes_qs.filter(obra_social=obra_filtro)

    return render(
        request,
        "turnos/pacientes_secretaria.html",
        {
            "config": config,
            "pacientes": pacientes_qs,
            "busqueda": busqueda,
            "obra_filtro": obra_filtro,
            "obras_sociales": Paciente.OBRAS_SOCIALES,
        },
    )


@login_required
@require_POST
def guardar_paciente_secretaria(request):
    """Permite crear o editar la ficha de un paciente desde el padrón de pacientes."""
    paciente_id = request.POST.get("paciente_id", "")
    nombre_completo = request.POST.get("nombre_completo", "").strip()
    dni = "".join(ch for ch in request.POST.get("dni", "") if ch.isdigit())
    telefono = request.POST.get("telefono", "").strip()
    email = request.POST.get("email", "").strip()
    obra_social = request.POST.get("obra_social", "Particular").strip()
    numero_afiliado = request.POST.get("numero_afiliado", "").strip()
    observaciones_medicas = request.POST.get("observaciones_medicas", "").strip()

    if not (nombre_completo and dni and telefono):
        messages.error(request, "Nombre completo, DNI y teléfono son obligatorios.")
        return redirect("pacientes_secretaria")

    if paciente_id:
        pac = get_object_or_404(Paciente, pk=paciente_id)
        pac.nombre_completo = nombre_completo
        pac.dni = dni
        pac.telefono = telefono
        pac.email = email
        pac.obra_social = obra_social
        pac.numero_afiliado = numero_afiliado
        pac.observaciones_medicas = observaciones_medicas
        pac.save()
        messages.success(request, f"Ficha clínica de {pac.nombre_completo} actualizada correctamente.")
    else:
        pac, creado = Paciente.objects.update_or_create(
            dni=dni,
            defaults={
                "nombre_completo": nombre_completo,
                "telefono": telefono,
                "email": email,
                "obra_social": obra_social,
                "numero_afiliado": numero_afiliado,
                "observaciones_medicas": observaciones_medicas,
            },
        )
        messages.success(request, f"Paciente {pac.nombre_completo} registrado en el padrón.")

    return redirect("pacientes_secretaria")


@login_required
@require_POST
def actualizar_configuracion_clinica(request):
    """Permite actualizar la dirección exacta de calle Belgrano, teléfono y horarios del consultorio."""
    config = ConfiguracionClinica.obtener()
    direccion = request.POST.get("direccion", "").strip()
    localidad = request.POST.get("localidad", "").strip()
    telefono_visible = request.POST.get("telefono_visible", "").strip()
    whatsapp_numero = "".join(ch for ch in request.POST.get("whatsapp_numero", "") if ch.isdigit())
    horario_atencion = request.POST.get("horario_atencion", "").strip()
    matricula = request.POST.get("matricula", "").strip()

    if direccion:
        config.direccion = direccion
    if localidad:
        config.localidad = localidad
    if telefono_visible:
        config.telefono_visible = telefono_visible
    if whatsapp_numero:
        config.whatsapp_numero = whatsapp_numero
    if horario_atencion:
        config.horario_atencion = horario_atencion
    if matricula:
        config.matricula = matricula
    config.save()

    messages.success(
        request,
        "Datos del consultorio (dirección en Calle Belgrano, teléfonos y horarios) actualizados en toda la web.",
    )
    return redirect("dashboard_secretaria")
