from django.contrib import admin
from .models import BloqueoAgenda, ConfiguracionClinica, Paciente, Tratamiento, Turno


@admin.register(ConfiguracionClinica)
class ConfiguracionClinicaAdmin(admin.ModelAdmin):
    list_display = ("nombre_clinica", "odontologa_titular", "direccion", "telefono_visible")


@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "duracion_minutos", "activo", "destacado", "orden")
    list_editable = ("duracion_minutos", "activo", "destacado", "orden")


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "dni", "telefono", "obra_social", "numero_afiliado")
    search_fields = ("nombre_completo", "dni", "telefono", "email")
    list_filter = ("obra_social",)


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "fecha", "hora", "paciente", "tratamiento", "estado", "origen", "es_sobreturno")
    list_filter = ("estado", "fecha", "origen", "tratamiento", "es_sobreturno")
    search_fields = ("codigo", "paciente__nombre_completo", "paciente__dni", "paciente__telefono")
    date_hierarchy = "fecha"


@admin.register(BloqueoAgenda)
class BloqueoAgendaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "todo_el_dia", "hora_inicio", "hora_fin", "motivo")
    list_filter = ("todo_el_dia", "fecha")
