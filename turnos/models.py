import random
import string
from datetime import time
from django.db import models


class ConfiguracionClinica(models.Model):
    nombre_clinica = models.CharField(
        max_length=150,
        default="Consultorio Odontológico Dra. Mariana Sánchez de Bustamante",
    )
    odontologa_titular = models.CharField(
        max_length=120,
        default="Dra. Mariana Sánchez de Bustamante",
    )
    especialidad_subtitulo = models.CharField(
        max_length=180,
        default="Odontología Integral, Estética Dental, Rehabilitación y Ortodoncia",
    )
    matricula = models.CharField(
        max_length=80,
        default="M.P. 14.892 — Especialista en Odontología Integral",
    )
    direccion = models.CharField(
        max_length=180,
        default="Calle Belgrano S/N (Altura a confirmar)",
        help_text="Dirección del consultorio (puede actualizar el número exacto de calle Belgrano aquí)",
    )
    localidad = models.CharField(
        max_length=120,
        default="Consultorio Planta Baja",
    )
    telefono_visible = models.CharField(
        max_length=50,
        default="+54 9 11 4582-9100",
    )
    whatsapp_numero = models.CharField(
        max_length=30,
        default="5491145829100",
        help_text="Sólo números con código de país para enlaces directos de WhatsApp",
    )
    email_contacto = models.EmailField(
        default="consultorio@dramarianabustamante.com.ar",
    )
    horario_atencion = models.CharField(
        max_length=220,
        default="Lunes a Viernes de 09:00 a 13:00 hs y 15:00 a 19:30 hs | Sábados de 09:00 a 12:30 hs",
    )

    class Meta:
        verbose_name = "Configuración del Consultorio"
        verbose_name_plural = "Configuración del Consultorio"

    def __str__(self):
        return f"{self.nombre_clinica} ({self.direccion})"

    @classmethod
    def obtener(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Tratamiento(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField()
    duracion_minutos = models.PositiveIntegerField(default=30)
    icono = models.CharField(max_length=50, default="tooth")
    color_tag = models.CharField(max_length=30, default="teal")
    destacado = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Tratamiento / Prestación"
        verbose_name_plural = "Tratamientos / Prestaciones"

    def __str__(self):
        return f"{self.nombre} ({self.duracion_minutos} min)"


class Paciente(models.Model):
    OBRAS_SOCIALES = [
        ("Particular", "Atención Particular"),
        ("OSDE", "OSDE"),
        ("Swiss Medical", "Swiss Medical"),
        ("Galeno", "Galeno"),
        ("Medifé", "Medifé"),
        ("Omint", "Omint"),
        ("Sancor Salud", "Sancor Salud"),
        ("Acord Salud", "Acord Salud"),
        ("IOMA / Provincial", "Obra Social Provincial / IOMA"),
        ("Otra Cobertura", "Otra Obra Social / Prepaga"),
    ]

    nombre_completo = models.CharField(max_length=140)
    dni = models.CharField(max_length=20, unique=True, db_index=True)
    telefono = models.CharField(max_length=40)
    email = models.EmailField(blank=True, default="")
    obra_social = models.CharField(
        max_length=60,
        choices=OBRAS_SOCIALES,
        default="Particular",
    )
    numero_afiliado = models.CharField(max_length=60, blank=True, default="")
    observaciones_medicas = models.TextField(
        blank=True,
        default="",
        help_text="Alergias, medicación, antecedentes relevantes o notas de secretaría",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre_completo"]
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self):
        return f"{self.nombre_completo} (DNI: {self.dni})"

    @property
    def telefono_whatsapp(self):
        solo_digitos = "".join(ch for ch in self.telefono if ch.isdigit())
        if not solo_digitos:
            return ""
        if not solo_digitos.startswith("54"):
            return f"549{solo_digitos.lstrip('0')}"
        return solo_digitos


class Turno(models.Model):
    ESTADO_PENDIENTE = "PENDIENTE"
    ESTADO_CONFIRMADO = "CONFIRMADO"
    ESTADO_EN_SALA = "EN_SALA"
    ESTADO_ATENDIDO = "ATENDIDO"
    ESTADO_CANCELADO = "CANCELADO"
    ESTADO_AUSENTE = "AUSENTE"

    ESTADOS_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente de Confirmar"),
        (ESTADO_CONFIRMADO, "Confirmado"),
        (ESTADO_EN_SALA, "En Sala de Espera"),
        (ESTADO_ATENDIDO, "Atendido"),
        (ESTADO_CANCELADO, "Cancelado"),
        (ESTADO_AUSENTE, "Ausente"),
    ]

    ORIGEN_WEB = "WEB"
    ORIGEN_SECRETARIA = "SECRETARIA"
    ORIGEN_WHATSAPP = "WHATSAPP"

    ORIGEN_CHOICES = [
        (ORIGEN_WEB, "Autogestión Web"),
        (ORIGEN_SECRETARIA, "Secretaría / Recepción"),
        (ORIGEN_WHATSAPP, "WhatsApp / Teléfono"),
    ]

    HORARIOS_BASE = [
        time(9, 0),
        time(9, 30),
        time(10, 0),
        time(10, 30),
        time(11, 0),
        time(11, 30),
        time(12, 0),
        time(12, 30),
        time(15, 0),
        time(15, 30),
        time(16, 0),
        time(16, 30),
        time(17, 0),
        time(17, 30),
        time(18, 0),
        time(18, 30),
        time(19, 0),
    ]

    HORARIOS_SABADO = [
        time(9, 0),
        time(9, 30),
        time(10, 0),
        time(10, 30),
        time(11, 0),
        time(11, 30),
        time(12, 0),
    ]

    codigo = models.CharField(max_length=15, unique=True, editable=False, db_index=True)
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="turnos",
    )
    tratamiento = models.ForeignKey(
        Tratamiento,
        on_delete=models.PROTECT,
        related_name="turnos",
    )
    fecha = models.DateField(db_index=True)
    hora = models.TimeField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_CHOICES,
        default=ESTADO_PENDIENTE,
        db_index=True,
    )
    origen = models.CharField(
        max_length=20,
        choices=ORIGEN_CHOICES,
        default=ORIGEN_WEB,
    )
    es_sobreturno = models.BooleanField(
        default=False,
        help_text="Permite a la secretaria asignar un turno adicional en un horario ocupado",
    )
    motivo_notas = models.TextField(
        blank=True,
        default="",
        help_text="Motivo de consulta o comentario ingresado por el paciente",
    )
    notas_secretaria = models.TextField(
        blank=True,
        default="",
        help_text="Observaciones internas de la secretaria o de la Dra. Mariana Sánchez de Bustamante",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fecha", "hora"]
        verbose_name = "Turno Odontológico"
        verbose_name_plural = "Turnos Odontológicos"

    def __str__(self):
        return f"[{self.codigo}] {self.fecha:%d/%m/%Y} {self.hora:%H:%M} - {self.paciente.nombre_completo}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._generar_codigo_unico()
        super().save(*args, **kwargs)

    @classmethod
    def _generar_codigo_unico(cls):
        while True:
            sufijo = "".join(random.choices(string.digits, k=4))
            codigo = f"MSB-{sufijo}"
            if not cls.objects.filter(codigo=codigo).exists():
                return codigo

    @classmethod
    def horarios_del_dia(cls, fecha_obj):
        dia_semana = fecha_obj.weekday()  # 0=Lunes ... 5=Sábado, 6=Domingo
        if dia_semana == 6:
            return []
        if dia_semana == 5:
            return cls.HORARIOS_SABADO
        return cls.HORARIOS_BASE


class BloqueoAgenda(models.Model):
    fecha = models.DateField(db_index=True)
    todo_el_dia = models.BooleanField(default=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    motivo = models.CharField(
        max_length=160,
        default="Congreso / Capacitación Dra. Mariana Sánchez de Bustamante",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Bloqueo de Agenda"
        verbose_name_plural = "Bloqueos de Agenda"

    def __str__(self):
        if self.todo_el_dia:
            return f"Día completo bloqueado: {self.fecha:%d/%m/%Y} ({self.motivo})"
        return f"Bloqueo {self.fecha:%d/%m/%Y} {self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M} ({self.motivo})"
