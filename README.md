# Consultorio Odontológico — Dra. Mariana Sánchez de Bustamante

Sistema web integral desarrollado en **Django** para la gestión de turnos odontológicos del consultorio de la **Dra. Mariana Sánchez de Bustamante** (Calle Belgrano).

## 🚀 Cómo iniciar el proyecto

Desde una terminal en esta carpeta (`E:\datos\Documentos\proyectoTurnosOdontologia`), ejecutá:

```powershell
python manage.py runserver
```

O hacé doble clic directamente en el archivo **`iniciar_demo.bat`**.

## 🔗 Accesos del Sistema

1. **Landing Page para Clientes / Pacientes (PC y Mobile):**
   - URL: `http://127.0.0.1:8000/`
   - Permite conocer el consultorio de la Dra. Mariana Sánchez de Bustamante en Calle Belgrano, ver tratamientos, consultar disponibilidad horaria en tiempo real, agendar un turno obteniendo un comprobante digital con código `MSB-XXXX` y consultar/cancelar turnos por DNI.

2. **Dashboard para la Secretaria y la Dra. Mariana:**
   - URL: `http://127.0.0.1:8000/secretaria/`
   - **Ingreso rápido con 1 clic** incluido en la pantalla de login para demostración inmediata, o mediante usuario y contraseña:
     - **Secretaría:** Usuario `secretaria` / Contraseña `belgrano2026`
     - **Dra. Mariana:** Usuario `mariana` / Contraseña `odontologia2026`

## ✨ Funcionalidades Principales

- **Reserva Online en 3 pasos con disponibilidad en tiempo real**: bloquea automáticamente los horarios ya tomados y separa Turno Mañana y Turno Tarde.
- **Dashboard de Secretaría**:
  - **KPIs en vivo del día**: Turnos del día, Pacientes en Sala de Espera, Confirmados, Pendientes de confirmar, Atendidos y Horarios Libres.
  - **Grilla Horaria Interactiva**: muestra todos los bloques de 09:00 a 19:00 hs con botón `+ Asignar` en horarios libres y `+ Sobreturno` en horarios ocupados.
  - **Carga Rápida de Turnos con Autocompletado por DNI**: cuando la secretaria escribe el DNI de un paciente existente, el sistema completa automáticamente su nombre, teléfono, obra social, número de afiliado y alertas médicas.
  - **Gestión en 1 Clic**: pasar a "En Sala de Espera", "Confirmar", "Marcar Atendido", "Cancelar", reprogramar fecha/hora o enviar recordatorio pre-redactado por **WhatsApp**.
  - **Configuración Editable de Calle Belgrano**: desde el botón `⚙️ Dirección / Horarios` del dashboard se puede actualizar en cualquier momento el número exacto de la calle Belgrano, el teléfono y los horarios de atención.
