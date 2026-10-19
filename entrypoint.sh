#!/bin/sh
set -e

# Asegurar que exista la carpeta persistente para la base de datos
mkdir -p /app/data

echo "Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

echo "Verificando datos iniciales de la Dra. Mariana Sánchez de Bustamante..."
python manage.py shell -c "from turnos.views import asegurar_datos_demo; asegurar_datos_demo()"

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor Gunicorn en el puerto ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
