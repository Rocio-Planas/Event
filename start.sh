#!/bin/bash
set -e

echo "==> Aplicando migraciones..."
python manage.py migrate --noinput

echo "==> Recogiendo archivos estáticos..."
python manage.py collectstatic --noinput

echo "==> Creando superusuario (si no existe)..."
python manage.py shell -c "
from usuarios.models import Usuario
if not Usuario.objects.filter(is_superuser=True).exists():
    Usuario.objects.create_superuser(
        email='rocioplanash@gmail.com',
        password='admin123'
    )
    print('Superusuario creado.')
else:
    print('El superusuario ya existe.')
"

echo "==> Arrancando Gunicorn..."
exec gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker --log-file -