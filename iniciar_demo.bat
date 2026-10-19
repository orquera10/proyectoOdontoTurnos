@echo off
title Sistema de Turnos Odontologia - Dra. Mariana Sanchez de Bustamante
cd /d "%~dp0"
echo ============================================================================
echo   CONSULTORIO ODONTOLOGICO - DRA. MARIANA SANCHEZ DE BUSTAMANTE
echo   Calle Belgrano - Sistema Web de Reserva de Turnos y Dashboard Secretaria
echo ============================================================================
echo.
echo   Iniciando servidor Django en:
echo   - Landing Page Pacientes:    http://127.0.0.1:8000/
echo   - Dashboard Secretaria:      http://127.0.0.1:8000/secretaria/
echo   - Panel Admin Django:        http://127.0.0.1:8000/admin/
echo.
start http://127.0.0.1:8000/
python manage.py runserver 0.0.0.0:8000
pause
