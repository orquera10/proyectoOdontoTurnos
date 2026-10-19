from django.urls import path
from . import views

urlpatterns = [
    # Interfaz Pública para Pacientes
    path("", views.landing_cliente, name="landing_cliente"),
    path("reservar/", views.reservar_turno_cliente, name="reservar_turno_cliente"),
    path("turno/<str:codigo>/", views.comprobante_turno, name="comprobante_turno"),
    path("turno/<str:codigo>/cancelar/", views.cancelar_turno_paciente, name="cancelar_turno_paciente"),
    # Endpoints AJAX / JSON
    path("api/horarios/", views.api_horarios_disponibles, name="api_horarios_disponibles"),
    path("api/consultar-turno/", views.api_consultar_turno, name="api_consultar_turno"),
    # Dashboard de Secretaría y Dra. Mariana Sánchez de Bustamante
    path("secretaria/login/", views.login_secretaria, name="login_secretaria"),
    path("secretaria/logout/", views.logout_secretaria, name="logout_secretaria"),
    path("secretaria/", views.dashboard_secretaria, name="dashboard_secretaria"),
    path("secretaria/turnos/crear/", views.crear_turno_secretaria, name="crear_turno_secretaria"),
    path(
        "secretaria/turnos/<int:turno_id>/estado/",
        views.cambiar_estado_turno,
        name="cambiar_estado_turno",
    ),
    path(
        "secretaria/turnos/<int:turno_id>/editar/",
        views.editar_turno_secretaria,
        name="editar_turno_secretaria",
    ),
    path("secretaria/pacientes/", views.pacientes_secretaria, name="pacientes_secretaria"),
    path(
        "secretaria/pacientes/guardar/",
        views.guardar_paciente_secretaria,
        name="guardar_paciente_secretaria",
    ),
    path(
        "secretaria/configuracion/actualizar/",
        views.actualizar_configuracion_clinica,
        name="actualizar_configuracion_clinica",
    ),
    path(
        "secretaria/api/paciente-dni/",
        views.api_buscar_paciente_dni,
        name="api_buscar_paciente_dni",
    ),
]
